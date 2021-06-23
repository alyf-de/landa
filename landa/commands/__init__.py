# Copyright (c) 2015, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import click
from getpass import getpass

import frappe
from frappe.commands import pass_context, get_site
from frappe.utils.data import today
from frappe.utils.password import update_password


@click.command('make-demo-accounts')
@click.argument('organization') #, help='Organization name, e.g. AVL-001')
@click.option('--dry-run', help='Don\'t commit the changes, just test the code.', is_flag=True)
@pass_context
def make_demo_accounts(context, organization, dry_run=False):
	"""Create Members, Meber Functions and Users for every Member Function Category."""
	site = get_site(context)
	password = getpass(prompt='Password for demo accounts: ')

	with frappe.init_site(site):
		frappe.connect()
		validate_organization(organization)
		mfc_list = frappe.get_all("Member Function Category", pluck='name')

		new_members = []
		for member_function_category in mfc_list:
			member = make_member(organization, member_function_category)
			if member:
				make_member_function(member.name, member_function_category)
				new_members.append(member)

		for member in new_members:
			update_password(member.user, password)

		if not dry_run:
			frappe.db.commit()
		
		if new_members:
			click.echo('The following users have been created:')
			for member in new_members:
				click.echo(member.user)


def validate_organization(organization: str):
	if not frappe.db.exists("Organization", organization):
		frappe.throw(f"No Organization named {organization}. Please create a new Organization or use an existing one.")

	doc = frappe.get_doc("Organization", organization)
	if len(doc.get_ancestors()) < 2:
		frappe.throw(f"{organization} is not a local organization.")


def make_member(organization: str, member_function_category: str):
	email = f"{scrub(member_function_category)}@example.org"
	if frappe.db.exists("User", email):
		click.echo(f"User {email} already exists.")
		return

	member = frappe.new_doc("LANDA Member")
	member.organization = organization
	member.create_user_account = 1
	member.first_name = f"Demo {member_function_category}"
	member.email = f"{scrub(member_function_category)}@example.org"

	member.save() # raises frappe.exceptions.OutgoingEmailError

	return member


def make_member_function(member: str, member_function_category: str):
	member_function = frappe.new_doc("Member Function")
	member_function.member = member
	member_function.member_function_category = member_function_category
	member_function.start_date = today()
	member_function.save()


def scrub(txt):
	umlauts = (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss'))

	words = txt.split()
	result = []
	for word in words:
		for source, target in umlauts:
			word = word.replace(source, target)
			word = word.replace(source.title(), target.title())
		
		word = ''.join(c for c in word if c.isalnum())
		word = word.lower()
		result.append(word)
	
	return '-'.join(result)


commands = [
	make_demo_accounts
]
