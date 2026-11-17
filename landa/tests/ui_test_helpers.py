import frappe
from frappe.tests.ui_test_helpers import whitelist_for_tests
from frappe.utils import today

from landa.organization_management.doctype.organization.organization import create_customer
from landa.utils import get_company_by_abbr

YEAR = 2030


@whitelist_for_tests
def create_sales_order_data():
	"""Create a regional organization (company), a local organization (customer),
	a user for each of them, and items for two years. Return the names that the
	UI tests need.
	"""
	# The default of a new site is a group, which a customer cannot use.
	frappe.db.set_default("customer_group", "Non Profit")

	state = get_or_create_organization("UI Test State Organization", short_code="UIS")
	regional = get_or_create_organization(
		"UI Test Regional Organization", short_code="UIR", parent_organization=state
	)
	company = get_company_by_abbr(regional)
	# A new customer takes the price list of its company. A Sales Order needs it to be saved.
	get_or_create_price_list("UI Test Price List", company)

	regional_office = get_or_create_regional_office("UI Test Regional Office", regional)
	local = get_or_create_local_organization("UI Test Local Organization", regional)

	# The tests save drafts. Remove the drafts of earlier runs.
	for sales_order in frappe.get_all("Sales Order", {"company": company, "docstatus": 0}, pluck="name"):
		frappe.delete_doc("Sales Order", sales_order)

	local_user = get_or_create_user(
		"ui-test-local@example.org", local, ["LANDA Local Organization Management"], "Local Organization"
	)
	regional_user = get_or_create_user(
		"ui-test-regional@example.org",
		regional_office,
		# "Sales User" gives access to the items, like in the standard categories.
		["LANDA Regional Organization Management", "Sales User"],
		"Regional Organization",
		member_administration=1,
	)
	mark_privacy_note_as_seen([local_user, regional_user])

	return {
		"local_user": local_user,
		"regional_user": regional_user,
		"company": company,
		"customer": local,
		"regional_office_customer": regional_office,
		"year": YEAR,
		"next_year": YEAR + 1,
		"items": [
			get_or_create_item(f"UI Test Item {YEAR}", company, YEAR),
			get_or_create_item(f"UI Test Second Item {YEAR}", company, YEAR),
		],
		"items_next_year": [get_or_create_item(f"UI Test Item {YEAR + 1}", company, YEAR + 1)],
	}


def get_or_create_local_organization(organization_name: str, regional_organization: str) -> str:
	local = get_or_create_organization(
		organization_name, parent_organization=regional_organization, is_group=0
	)

	# The organization creates its customer in a background job. Do not wait for it.
	create_customer(local, organization_name)

	return local


def get_or_create_regional_office(organization_name: str, regional_organization: str) -> str:
	"""Return the organization for the members of the regional organization itself.

	Its number is 000. It is the default customer of its members.
	"""
	# Only an import can set the name of an organization.
	frappe.flags.in_import = True
	regional_office = get_or_create_organization(
		organization_name,
		name=f"{regional_organization}-000",
		parent_organization=regional_organization,
		is_group=0,
	)
	frappe.flags.in_import = False

	create_customer(regional_office, organization_name)

	return regional_office


@whitelist_for_tests
def clear_default_customer(user: str):
	"""Remove the default customer that LANDA sets for `user` on each login."""
	frappe.defaults.clear_user_default("customer", user=user)


def get_or_create_organization(organization_name: str, is_group: int = 1, **kwargs) -> str:
	existing_organization = frappe.db.exists("Organization", {"organization_name": organization_name})
	if existing_organization:
		return existing_organization

	organization = frappe.new_doc("Organization")
	organization.organization_name = organization_name
	organization.is_group = is_group
	organization.update(kwargs)
	organization.insert()

	return organization.name


def get_or_create_price_list(price_list_name: str, company: str) -> str:
	"""Return a selling price list of `company`."""
	if frappe.db.exists("Price List", price_list_name):
		return price_list_name

	price_list = frappe.new_doc("Price List")
	price_list.price_list_name = price_list_name
	price_list.currency = "EUR"
	price_list.selling = 1
	price_list.company = company
	price_list.insert()

	return price_list.name


def get_or_create_item(item_name: str, company: str, year: int) -> str:
	"""Return an item that can be ordered for `company` in `year` only."""
	existing_item = frappe.db.exists("Item", {"item_name": item_name})
	if existing_item:
		return existing_item

	item = frappe.new_doc("Item")
	item.item_name = item_name  # LANDA sets the item code
	item.item_group = frappe.db.get_value("Item Group", {"is_group": 0})
	item.stock_uom = "Anzahl"
	item.is_stock_item = 0
	item.company = company
	item.valid_from_year = year
	item.valid_to_year = year
	item.insert()

	return item.name


def get_or_create_user(
	email: str, organization: str, roles: list[str], access_level: str, member_administration: int = 0
) -> str:
	"""Return a user who is a member of `organization` and gets `roles` from a member function.

	With `member_administration`, the user can access the organization at `access_level`
	and the organizations below it.

	The password is the administrator password, like for the test user of Frappe.
	"""
	if frappe.db.exists("User", email):
		return email

	member = frappe.new_doc("LANDA Member")
	member.organization = organization
	member.first_name = "UI Test"
	member.last_name = roles[0]
	member.insert()

	member_function = frappe.new_doc("Member Function")
	member_function.member = member.name
	member_function.member_function_category = get_or_create_member_function_category(
		roles, access_level, member_administration
	)
	member_function.start_date = today()
	member_function.insert()

	user = frappe.new_doc("User")
	user.email = email
	user.first_name = member.first_name
	user.last_name = member.last_name
	user.landa_member = member.name
	user.organization = organization
	user.language = "en"  # the UI tests find some buttons by their label
	user.send_welcome_email = 0
	user.new_password = frappe.conf.admin_password or "admin"
	user.flags.ignore_password_policy = True
	user.insert()

	return user.name


def mark_privacy_note_as_seen(users: list[str]):
	"""The privacy note opens on each login until the user has read it.

	`bench migrate` imports the note again and removes its readers.
	"""
	privacy_note = frappe.get_doc("Note", "Datenschutz Hinweise")
	readers = [reader.user for reader in privacy_note.seen_by]
	for user in users:
		if user not in readers:
			privacy_note.append("seen_by", {"user": user})

	privacy_note.save()


def get_or_create_member_function_category(
	roles: list[str], access_level: str, member_administration: int
) -> str:
	category_name = f"UI Test {roles[0]}"
	if frappe.db.exists("Member Function Category", category_name):
		return category_name

	category = frappe.new_doc("Member Function Category")
	category.name = category_name
	category.access_level = access_level
	category.member_administration = member_administration
	for role in roles:
		category.append("roles", {"role": role})
	category.insert()

	return category.name
