import frappe
from frappe import _
from pypika.functions import Sum

from landa.water_body_management.report.utils import add_or_filters


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

	query = (
		frappe.qb.from_(entry)
		.join(organization)
		.on(entry.organization == organization.name)
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
		query = query.where(entry.organization == selected_organization)

	query = add_or_filters(query, entry)
	return query.run(as_dict=True)
