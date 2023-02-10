import frappe
from frappe import _
from frappe.utils.nestedset import get_ancestors_of
from contextlib import contextmanager


def get_new_name(prefix, company, doctype):
	"""
	Create a document name like prefix-company-year-####.

	For example 'ZAHL-AVS-2021-0001'.
	"""
	from frappe.model.naming import make_autoname
	from frappe.utils.data import nowdate

	company_abbr = frappe.get_value("Company", company, "abbr")
	current_year = nowdate()[:4]  # note: y10k problem
	return make_autoname(f"{prefix}-{company_abbr}-{current_year}-.####", doctype)


def welcome_email():
	lang = frappe.db.get_single_value("System Settings", "language")
	site_name = "LANDA"
	title = _("Welcome to {0}", lang=lang).format(site_name)
	return title


def reset_workspace(workspace: str) -> None:
	"""Delete all user's custom extensions of `workspace`.

	Used to reset user customizations after the workspace definition has changed."""
	custom_workspaces = frappe.get_all(
		"Workspace",
		filters={"for_user": ("is", "set"), "extends": workspace},
		pluck="name",
	)
	for workspace_name in custom_workspaces:
		frappe.delete_doc("Workspace", workspace_name)


def get_current_member_data() -> frappe._dict:
	result = frappe._dict()
	if not frappe.session.user or (frappe.session.user in frappe.STANDARD_USERS):
		return result

	# TODO: Something if off with the cache -> loading old data. Figure out reason before reactivating.
	# from_cache = frappe.cache().hget("landa", frappe.session.user)
	# if from_cache:
	#	return from_cache

	member_name, member_organization = get_member_and_organization(frappe.session.user)

	if not member_name:
		frappe.cache().hset("landa", frappe.session.user, result)
		return result

	if not member_organization:
		# drop dash and 4 member number digits
		# "AVL-001-0001" -> "AVL-001
		member_organization = member_name[:-5]

	ancestors = get_ancestors_of("Organization", member_organization)
	ancestors.reverse()  # root as the first element

	result.member = member_name
	result.organization = member_organization
	result.local_organization = ancestors[2] if len(ancestors) > 2 else member_organization
	result.regional_organization = ancestors[1]
	result.company = get_company_by_abbr(ancestors[1])
	result.state_organization = ancestors[0]

	frappe.cache().hset("landa", frappe.session.user, result)

	return result


@contextmanager
def autocommit():
	flag_value = frappe.db.auto_commit_on_many_writes
	frappe.db.auto_commit_on_many_writes = True
	yield
	frappe.db.auto_commit_on_many_writes = flag_value


def get_default_company(organization: str):
	"""Return the company associated to the organization's regional organization."""
	doc = frappe.get_doc("Organization", organization)
	ancestors = doc.get_ancestors()

	if len(ancestors) < 2:
		return None

	ancestors.reverse()

	return get_company_by_abbr(ancestors[1])


def get_company_by_abbr(abbr: str):
	"""Return the company name based on it's abbreviation."""
	return frappe.db.get_value("Company", {"abbr": abbr})


def get_member_and_organization(user: str) -> tuple:
	"""Return the LANDA Member and Organization linked in the user."""
	return frappe.db.get_value("User", user, fieldname=["landa_member", "organization"])


def update_doc(source_doc, target_doc):
	FIELD_MAPPINGS = {
		"Sales Order": {
			"billing_address": "customer_address",
			"billing_address_display": "address_display",
			"billing_contact": "contact_person",
			"billing_contact_display": "contact_display",
			"billing_contact_email": "contact_email",
			"billing_contact_mobile": "contact_mobile",
			"billing_contact_phone": "contact_phone",
			"shipping_address": "shipping_address_name",
			"shipping_address_display": "shipping_address",
			"shipping_contact": "shipping_contact",
			"shipping_contact_display": "shipping_contact_display",
			"shipping_contact_email": "shipping_contact_email",
			"shipping_contact_mobile": "shipping_contact_mobile",
			"shipping_contact_phone": "shipping_contact_phone",
		},
		"Sales Invoice": {
			"billing_address": "customer_address",
			"billing_address_display": "address_display",
			"billing_contact": "contact_person",
			"billing_contact_display": "contact_display",
			"billing_contact_email": "contact_email",
			"billing_contact_mobile": "contact_mobile",
			"billing_contact_phone": "contact_phone",
			"shipping_address": "shipping_address_name",
			"shipping_address_display": "shipping_address",
			"shipping_contact": "shipping_contact",
			"shipping_contact_display": "shipping_contact_display",
			"shipping_contact_email": "shipping_contact_email",
			"shipping_contact_mobile": "shipping_contact_mobile",
			"shipping_contact_phone": "shipping_contact_phone",
		},
		"Delivery Note": {
			"billing_address": "customer_address",
			"billing_address_display": "address_display",
			"billing_contact": "billing_contact",
			"billing_contact_display": "billing_contact_display",
			"billing_contact_email": "billing_contact_email",
			"billing_contact_mobile": "billing_contact_mobile",
			"billing_contact_phone": "billing_contact_phone",
			"shipping_address": "shipping_address_name",
			"shipping_address_display": "shipping_address",
			"shipping_contact": "contact_person",
			"shipping_contact_display": "contact_display",
			"shipping_contact_email": "contact_email",
			"shipping_contact_mobile": "contact_mobile",
			"shipping_contact_phone": "contact_phone",
		},
	}

	fields = {}
	
	for key, source_field_name in FIELD_MAPPINGS[source_doc.doctype].items():
		target_field_name = FIELD_MAPPINGS[target_doc.doctype][key]
		fields[target_field_name] = getattr(source_doc, source_field_name)

	target_doc.update(fields)
