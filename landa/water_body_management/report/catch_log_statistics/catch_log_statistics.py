# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from landa.organization_management.doctype.member_function_category.member_function_category import (
	get_organization_at_level,
)


STATE_ROLES = {"LANDA State Organization Employee", "System Manager", "Administrator"}
REGIONAL_ROLES = {
	"LANDA Regional Organization Management",
	"LANDA Regional Water Body Management",
}
LOCAL_ROLES = {"LANDA Local Water Body Management"}

COLUMNS = [
	{
		"fieldname": "catch_log_entry",
		"fieldtype": "Link",
		"label": "Catch Log Entry",
		"options": "Catch Log Entry",
	},
	{
		"fieldname": "year",
		"fieldtype": "Data",
		"label": "Year",
	},
	{
		"fieldname": "water_body",
		"fieldtype": "Link",
		"label": "Water Body",
		"options": "Water Body",
	},
	{
		"fieldname": "fishing_area",
		"fieldtype": "Link",
		"label": "Fishing Area",
		"options": "Fishing Area",
	},
	{
		"fieldname": "organization",
		"fieldtype": "Data",
		"label": "Organization",
		"options": "Organization",
	},
	{
		"fieldname": "origin_of_catch_log_entry",
		"fieldtype": "Data",
		"label": "Origin of Catch Log Entry",
	},
	{
		"fieldname": "number_of_catch_log_books",
		"fieldtype": "Int",
		"label": "Number of Catch Log Books",
	},
	{
		"fieldname": "fishing_days",
		"fieldtype": "Int",
		"label": "Fishing Days",
	},
	{
		"fieldname": "fish_species",
		"fieldtype": "Link",
		"label": "Fish Species",
		"options": "Fish Species",
	},
	{
		"fieldname": "amount",
		"fieldtype": "Int",
		"label": "Number of Fish",
	},
	{
		"fieldname": "weight_in_kg",
		"fieldtype": "Float",
		"label": "Weight in Kg",
	},
]


def get_data(filters):
	filters["workflow_state"] = "Approved"

	user_roles = set(frappe.get_roles())
	or_filters = {}

	if not user_roles.intersection(STATE_ROLES):
		# User is not a state organization employee
		member_name, member_organization = frappe.db.get_value(
			"LANDA Member",
			filters={"user": frappe.session.user},
			fieldname=["name", "organization"],
		)
		if user_roles.intersection(REGIONAL_ROLES):
			regional_organization = get_organization_at_level(
				member_name, 1, member_organization
			)
			filters["regional_organization"] = regional_organization
		else:
			# User is not in regional organization management
			or_filters["water_body"] = ("in", get_supported_water_bodies(member_organization))
			or_filters["organization"] = member_organization

	data = frappe.get_all(
		"Catch Log Entry",
		fields=[
			"name",
			"year",
			"water_body",
			"fishing_area",
			"organization",
			"origin_of_catch_log_entry",
			"number_of_catch_log_books",
			"fishing_days",
			"`tabCatch Log Fish Table`.fish_species",
			"`tabCatch Log Fish Table`.amount",
			"`tabCatch Log Fish Table`.weight_in_kg",
		],
		filters=filters,
		or_filters=or_filters,
	)

	def postprocess(row):
		row["year"] = str(row.get("year"))	# avoid year getting summed up
		return list(row.values())

	return [postprocess(row) for row in data]


def get_supported_water_bodies(organization):
	"""Return a list of water bodies that are supported by the organization."""
	return frappe.get_all("Water Body Management Local Organization", filters={"organization": organization}, pluck="water_body")


def execute(filters=None):
	return COLUMNS, get_data(filters)
