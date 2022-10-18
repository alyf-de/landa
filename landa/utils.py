import frappe
from frappe import _
from frappe.utils.nestedset import get_ancestors_of


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


def get_current_member_data():
	from_cache = frappe.cache().hget("landa", frappe.session.user)
	if from_cache:
		return from_cache

	result = frappe._dict()
	data = frappe.db.get_value(
		"LANDA Member",
		filters={"user": frappe.session.user},
		fieldname=["name", "organization"],
	)

	if not data:
		frappe.cache().hset("landa", frappe.session.user, result)
		return result

	member_name, member_organization = data
	member_organization = member_organization[
		:7
	]  # use local Organization instead of Ortsgruppe

	ancestors = get_ancestors_of("Organization", member_organization)
	ancestors.reverse()	 # root as the first element

	result.member = member_name
	result.local_organization = member_organization
	result.regional_organization = ancestors[1]
	result.state_organization = ancestors[0]

	frappe.cache().hset("landa", frappe.session.user, result)

	return result


def db_unset(doctype: str, field: str, value: str) -> None:
	"""In all records of `doctype` where `field` is equal to `value`, set field to `None`."""
	table = frappe.qb.DocType(doctype)
	frappe.qb.update(table).set(table[field], None).where(table[field] == value).run()


def remove_from_table(
	parent_doctype: str, table_field: str, table_filters: "dict[str, str]"
):
	"""Remove rows matching `table_filters` from `table_field` of `parent_doctype`.

	For example, we can remove a User from the Seen By table of all Notes like this:

	`remove_from_table("Note", "seen_by", {"user": "mail@example.org"})`
	"""
	table_doctype = frappe.get_meta(parent_doctype).get_field(table_field).options
	table = frappe.qb.DocType(table_doctype)
	query = frappe.qb.from_(table).select(table.parent, table.idx).distinct()

	if not table_filters:
		table_filters = {}

	table_filters["parenttype"] = parent_doctype

	for key, value in table_filters.items():
		query = query.where(table[key] == value)

	for name, idx in query.run():
		doc = frappe.get_doc(parent_doctype, name)
		doc.get(table_field).pop(idx - 1)
		doc.save(ignore_permissions=True)


