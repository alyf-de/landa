# Copyright (c) 2015, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import click
from getpass import getpass

import frappe
from frappe.commands import pass_context, get_site
from frappe.utils.data import today
from frappe.utils.password import update_password


@click.command('make-demo-accounts')
@click.argument('organization')
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

		new_users = []
		for member_function_category in mfc_list:
			email = f"{scrub(member_function_category)}@example.org"
			first_name = f"Demo {member_function_category}"

			member_name = create_member(organization, member_function_category)
			make_member_function(member_name, member_function_category)

			user_name = create_user(email, first_name, member_name, organization)
			update_password(user_name, password)
			new_users.append(user_name)

		if not dry_run:
			frappe.db.commit()
		
		if new_users:
			click.echo('The following users have been created:')
			for user in new_users:
				click.echo(user)


@click.command("update-organization-series")
@click.option(
	"--dry-run", help="Don't commit the changes, just test the code.", is_flag=True
)
@pass_context
def update_organization_series(context, dry_run=False):
	# frappe.local.flags.in_test = True	 # avoid permission check
	site = get_site(context)

	with frappe.init_site(site):
		frappe.connect()

		for organization in frappe.get_all(
			"Organization", filters={"name": ("!=", "LV")}, pluck="name"
		):
			doc = frappe.get_doc("Organization", organization)
			if doc.is_group:
				highest_number = frappe.get_all(
					"Organization",
					filters={
						"parent_organization": organization,
						"name": ("not in", ("AVL", "AVS", "AVE")),
					},
					pluck="name",
					order_by="name desc",
					limit=1,
				)
			else:
				highest_number = frappe.get_all(
					"LANDA Member",
					filters={
						"organization": organization,
					},
					pluck="name",
					order_by="name desc",
					limit=1,
				)

			if not highest_number:
				continue

			highest_number = highest_number[0]

			# security check -- don't do stupid things
			if organization != highest_number[: len(organization)]:
				click.echo(f"Could not update series for {organization}.")
				continue

			highest_number = int(highest_number.split("-")[-1])
			doc.set_series_current(highest_number)

		if not dry_run:
			frappe.db.commit()


def validate_organization(organization: str):
	if not frappe.db.exists("Organization", organization):
		frappe.throw(f"No Organization named {organization}. Please create a new Organization or use an existing one.")

	doc = frappe.get_doc("Organization", organization)
	if len(doc.get_ancestors()) < 2:
		frappe.throw(f"{organization} is not a local organization.")


def create_member(organization: str, member_function_category: str) -> str:
	member = frappe.new_doc("LANDA Member")
	member.organization = organization
	member.first_name = f"Demo {member_function_category}"
	member.save()

	return member.name


def create_user(email: str, first_name: str, member: str, organization: str) -> str:
	if frappe.db.exists("User", email):
		click.echo(f"User {email} already exists.")
		return

	user = frappe.new_doc("User")
	user.email = email
	user.first_name = first_name
	user.landa_member = member
	user.organization = organization
	user.save()

	return user.name


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


commands = [make_demo_accounts, update_organization_series]
