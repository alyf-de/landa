import frappe
from frappe import _
from pypika.functions import Sum

from landa.utils import get_current_member_data
from landa.water_body_management.report.utils import REGIONAL_ROLES, STATE_ROLES, get_user_roles


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"label": _("Organization"),
			"options": "Organization",
			"width": 130,
		},
		{
			"fieldname": "organization_name",
			"fieldtype": "Data",
			"label": _("Organization Name"),
			"width": 250,
		},
		{
			"fieldname": "fishing_days",
			"fieldtype": "Int",
			"label": _("Fishing Days"),
			"width": 120,
		},
	]


def get_data(filters):
	entry = frappe.qb.DocType("Catch Log Entry")
	organization = frappe.qb.DocType("Organization")

	# Join Organization for the current name, the name stored on the entry may be outdated
	query = (
		frappe.qb.from_(entry)
		.join(organization)
		.on(organization.name == entry.organization)
		.select(
			entry.organization,
			organization.organization_name,
			Sum(entry.fishing_days).as_("fishing_days"),
		)
		.where(entry.workflow_state == "Approved")
		.groupby(entry.organization, organization.organization_name)
		.orderby(Sum(entry.fishing_days), order=frappe.qb.desc)
		.orderby(organization.organization_name)
	)

	water_body = filters.get("water_body")
	if not water_body:
		frappe.throw(_("{0} is mandatory").format(_("Water Body")))

	query = query.where(entry.water_body == water_body)

	if from_year := filters.get("from_year"):
		query = query.where(entry.year >= from_year)
	if to_year := filters.get("to_year"):
		query = query.where(entry.year <= to_year)
	if selected_organization := filters.get("organization"):
		# Include the local groups of the selected club
		query = query.where(
			(entry.organization == selected_organization)
			| entry.organization.like(f"{selected_organization}-%")
		)

	return restrict_to_own_clubs(query, entry).run(as_dict=True)


def restrict_to_own_clubs(query, entry):
	"""State roles see all clubs. Regional roles see only the clubs of their own
	regional organization, not other clubs fishing on their water bodies. All
	other roles are denied, even if they get access to the report later."""
	user_roles = get_user_roles()
	if STATE_ROLES.intersection(user_roles):
		return query

	if not REGIONAL_ROLES.intersection(user_roles):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	member_data = get_current_member_data()
	if not member_data:
		frappe.throw(_("You are not a member of any organization."))

	return query.where(entry.organization.like(f"{member_data.regional_organization}-%"))
