# Copyright (c) 2015, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import json
from getpass import getpass
from typing import Dict, List

import click
import frappe
from frappe.commands import get_site, pass_context
from frappe.utils import update_progress_bar
from frappe.utils.data import today
from frappe.utils.password import update_password


@click.command("make-demo-accounts")
@click.argument("organization")
@click.option("--dry-run", help="Don't commit the changes, just test the code.", is_flag=True)
@pass_context
def make_demo_accounts(context, organization, dry_run=False):
	"""Create Members, Member Functions and Users for every Member Function Category."""
	site = get_site(context)
	password = getpass(prompt="Password for demo accounts: ")

	with frappe.init_site(site):
		frappe.connect()
		validate_organization(organization)

		new_users = []
		for member_function_category in frappe.get_all("Member Function Category", pluck="name"):
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
			click.echo("The following users have been created:\n")
			for user in new_users:
				click.echo(user)


@click.command("update-organization-series")
@click.option("--dry-run", help="Don't commit the changes, just test the code.", is_flag=True)
@pass_context
def update_organization_series(context, dry_run=False):
	# frappe.local.flags.in_test = True	 # avoid permission check
	site = get_site(context)

	with frappe.init_site(site):
		frappe.connect()

		for organization in frappe.get_all("Organization", filters={"name": ("!=", "LV")}, pluck="name"):
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


@click.command("import-geojson")
@click.argument(
	"geojson_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True, readable=True)
)
@pass_context
def import_geojson(context, geojson_file):
	"""Import GeoJSON file into the database."""
	with open(geojson_file) as f:
		data = json.load(f)

	site = get_site(context)
	with frappe.init_site(site):
		frappe.connect()
		import_features(data.get("features", []))
		frappe.db.commit()


def import_features(features: List[Dict]) -> None:
	not_found = []
	total_feautres = len(features)
	for i, feature in enumerate(features, start=1):
		update_progress_bar("Importing GeoJSON", i, total_feautres)
		water_body_id = feature.get("properties", {}).get("GEW_ID")
		if not water_body_id:
			continue

		if not frappe.db.exists("Water Body", water_body_id):
			not_found.append(water_body_id)
			continue

		feature["properties"].pop("GEW_ID")
		feature["properties"].pop("GEW_NA")

		frappe.db.set_value(
			"Water Body",
			water_body_id,
			"location",
			json.dumps({"type": "FeatureCollection", "features": [feature]}),
		)

	if not_found:
		click.echo(f"\nCould not find the following Water Bodies in LANDA: {', '.join(not_found)}")


def validate_organization(organization: str):
	if not frappe.db.exists("Organization", organization):
		frappe.throw(
			f"No Organization named {organization}. Please create a new Organization or use an existing one."
		)

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
		return email

	user = frappe.new_doc("User")
	user.email = email
	user.first_name = first_name
	user.landa_member = member
	user.organization = organization
	user.send_welcome_email = 0
	user.save()

	return user.name


def make_member_function(member: str, member_function_category: str):
	member_function = frappe.new_doc("Member Function")
	member_function.member = member
	member_function.member_function_category = member_function_category
	member_function.start_date = today()
	member_function.save()


def scrub(txt):
	umlauts = (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"))

	words = txt.split()
	result = []
	for word in words:
		for source, target in umlauts:
			word = word.replace(source, target)
			word = word.replace(source.title(), target.title())

		word = "".join(c for c in word if c.isalnum())
		word = word.lower()
		result.append(word)

	return "-".join(result)


commands = [make_demo_accounts, update_organization_series, import_geojson]
