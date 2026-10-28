import frappe
from frappe import _
from pypika.functions import Sum

from landa.utils import get_current_member_data
from landa.water_body_management.report.utils import STATE_ROLES, get_user_roles


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

	if water_body := filters.get("water_body"):
		query = query.where(entry.water_body == water_body)
	if from_year := filters.get("from_year"):
		query = query.where(entry.year >= from_year)
	if to_year := filters.get("to_year"):
		query = query.where(entry.year <= to_year)
	if selected_organization := filters.get("organization"):
		# Include the local groups of the selected club
		query = query.where(entry.organization.like(f"{selected_organization}%"))

	# Regional organizations may only see their own clubs, not other clubs fishing on their water bodies
	if not STATE_ROLES.intersection(get_user_roles()):
		regional_organization = get_current_member_data().regional_organization
		query = query.where(entry.organization.like(f"{regional_organization}-%"))

	return query.run(as_dict=True)
