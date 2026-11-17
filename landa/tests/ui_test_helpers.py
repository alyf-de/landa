import frappe
from frappe.tests.ui_test_helpers import whitelist_for_tests
from frappe.utils import today

from landa.organization_management.doctype.organization.organization import create_customer
from landa.utils import get_default_company

YEAR = 2030


@whitelist_for_tests
def create_sales_order_data():
	"""Create a regional organization (company), a local organization (customer)
	with a user, and one item for each of two years. Return the names that the
	UI test needs.
	"""
	# The default of a new site is a group, which a customer cannot use.
	frappe.db.set_default("customer_group", "Non Profit")

	state = get_or_create_organization("UI Test State Organization", short_code="UIS")
	regional = get_or_create_organization(
		"UI Test Regional Organization", short_code="UIR", parent_organization=state
	)
	local = get_or_create_organization("UI Test Local Organization", parent_organization=regional, is_group=0)

	# The organization creates its customer in a background job. Do not wait for it.
	create_customer(local, "UI Test Local Organization")

	company = get_default_company(local)

	return {
		"user": get_or_create_user("ui-test-local@example.org", local, "LANDA Local Organization Management"),
		"company": company,
		"customer": local,
		"year": YEAR,
		"next_year": YEAR + 1,
		"item": get_or_create_item(f"UI Test Item {YEAR}", company, YEAR),
		"item_next_year": get_or_create_item(f"UI Test Item {YEAR + 1}", company, YEAR + 1),
	}


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


def get_or_create_user(email: str, organization: str, role: str) -> str:
	"""Return a user who is a member of `organization` and gets `role` from a member function.

	The password is the administrator password, like for the test user of Frappe.
	"""
	if frappe.db.exists("User", email):
		return email

	member = frappe.new_doc("LANDA Member")
	member.organization = organization
	member.first_name = "UI Test"
	member.last_name = role
	member.insert()

	member_function = frappe.new_doc("Member Function")
	member_function.member = member.name
	member_function.member_function_category = get_or_create_member_function_category(role)
	member_function.start_date = today()
	member_function.insert()

	user = frappe.new_doc("User")
	user.email = email
	user.first_name = member.first_name
	user.last_name = member.last_name
	user.landa_member = member.name
	user.organization = organization
	user.send_welcome_email = 0
	user.new_password = frappe.conf.admin_password or "admin"
	user.flags.ignore_password_policy = True
	user.insert()

	# The privacy note opens on each login until the user has read it.
	privacy_note = frappe.get_doc("Note", "Datenschutz Hinweise")
	privacy_note.append("seen_by", {"user": user.name})
	privacy_note.save()

	return user.name


def get_or_create_member_function_category(role: str) -> str:
	category_name = f"UI Test {role}"
	if frappe.db.exists("Member Function Category", category_name):
		return category_name

	category = frappe.new_doc("Member Function Category")
	category.name = category_name
	category.access_level = "Local Organization"
	category.append("roles", {"role": role})
	category.insert()

	return category.name
