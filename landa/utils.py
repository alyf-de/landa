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
