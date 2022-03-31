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

	data = frappe.get_all(
		"Catch Log Entry",
		fields=[
			"name",
			"year",
			"water_body",
			"fishing_area",
			"organization",
			"origin_of_catch_log_entry",
			"`tabCatch Log Fish Table`.fish_species",
			"`tabCatch Log Fish Table`.amount",
			"`tabCatch Log Fish Table`.weight_in_kg",
		],
		filters=filters,
		or_filters=get_or_filters(),
	)

	def postprocess(row):
		row["year"] = str(row.get("year"))	# avoid year getting summed up
		return list(row.values())

	return [postprocess(row) for row in data]


def get_or_filters():
	"""Return a dict of filters that restricts the results to what the user is
	allowed to see.

	STATE_ROLES		no filters
	REGIONAL_ROLES	everything related to their water bodys OR to their member
					organizations
	LOCAL_ROLES		everything related to their own organization and OR to the
					water bodys it is supporting
	"""
	or_filters = {}
	user_roles = set(frappe.get_roles())

	if user_roles.intersection(STATE_ROLES):
		return or_filters

	# User is not a state organization employee
	member_name, member_organization = frappe.db.get_value(
		"LANDA Member",
		filters={"user": frappe.session.user},
		fieldname=["name", "organization"],
	)
	member_organization = member_organization[
		:7
	]  # use local Organization instead of Ortsgruppe

	if user_roles.intersection(REGIONAL_ROLES):
		regional_organization = get_organization_at_level(
			member_name, 1, member_organization
		)
		or_filters["regional_organization"] = regional_organization
		or_filters["organization"] = ("like", f"{regional_organization}-%")
	else:
		# User is not in regional organization management
		or_filters["water_body"] = (
			"in",
			get_supported_water_bodies(member_organization),
		)
		or_filters["organization"] = member_organization

	return or_filters


def get_supported_water_bodies(organization):
	"""Return a list of water bodies that are supported by the organization."""
	return frappe.get_all(
		"Water Body Management Local Organization",
		filters={"organization": organization},
		pluck="water_body",
	)


def execute(filters=None):
	return COLUMNS, get_data(filters)
