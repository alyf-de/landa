# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from landa.water_body_management.report.catch_log_statistics.catch_log_statistics import (
	get_or_filters,
)


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
		"fieldname": "fishing_days",
		"fieldtype": "Int",
		"label": "Fishing Days",
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
			"fishing_days",
		],
		filters=filters,
		or_filters=get_or_filters(),
	)

	def postprocess(row):
		row["year"] = str(row.get("year"))	# avoid year getting summed up
		return list(row.values())

	return [postprocess(row) for row in data]


def execute(filters=None):
	return COLUMNS, get_data(filters)
