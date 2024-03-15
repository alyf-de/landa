# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from landa.organization_management.doctype.organization.organization import (
	get_supported_water_bodies,
)
from landa.utils import get_current_member_data
from landa.water_body_management.report.catch_log_statistics.catch_log_statistics import (
	REGIONAL_ROLES,
	STATE_ROLES,
)

COLUMNS = [
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
		"fieldname": "water_body_title",
		"fieldtype": "Data",
		"label": "Water Body Title",
		"width": 200,
	},
	{
		"fieldname": "fishing_days",
		"fieldtype": "Int",
		"label": "Fishing Days",
	},
]


def get_data(filters):
	filters["workflow_state"] = "Approved"

	water_bodies = filters.pop("water_body", [])
	fishing_areas = filters.pop("fishing_area", [])

	if water_bodies:
		filters["water_body"] = ("in", water_bodies)

	if fishing_areas:
		filters["fishing_area"] = ("in", fishing_areas)

	data = frappe.get_all(
		"Catch Log Entry",
		fields=[
			"year",
			"water_body",
			"water_body_title",
			"SUM(fishing_days)",
		],
		filters=filters,
		or_filters=get_or_filters(),
		group_by="year,water_body,water_body_title",
	)

	def postprocess(row):
		row["year"] = str(row.get("year"))  # avoid year getting summed up
		return list(row.values())

	return [postprocess(row) for row in data]


def execute(filters=None):
	return COLUMNS, get_data(filters)


def get_or_filters():
	"""Return a dict of filters that restricts the results to what the user is
	allowed to see.
	STATE_ROLES		no filters
	REGIONAL_ROLES	everything related to their water bodys OR to their member organizations
	LOCAL_ROLES		everything related to their own organization and OR to the water bodys it is supporting
	"""
	or_filters = {}
	user_roles = set(frappe.get_roles())

	if user_roles.intersection(STATE_ROLES):
		return or_filters

	# User is not a state organization employee
	member_data = get_current_member_data()
	if not member_data:
		frappe.throw(_("You are not a member of any organization."))

	if user_roles.intersection(REGIONAL_ROLES):
		or_filters["regional_organization"] = member_data.regional_organization
		or_filters["organization"] = ("like", f"{member_data.regional_organization}-%")
	else:
		# User is not in regional organization management
		or_filters["water_body"] = (
			"in",
			get_supported_water_bodies(member_data.local_organization),
		)
		or_filters["organization"] = member_data.local_organization

	return or_filters
