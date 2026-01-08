# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	if filters.get("group_by_member"):
		return [
			{
				"label": _("Member"),
				"fieldname": "member",
				"fieldtype": "Link",
				"options": "LANDA Member",
				"width": 150,
			},
			{
				"label": _("Member Name"),
				"fieldname": "member_name",
				"fieldtype": "Data",
				"width": 200,
			},
			{
				"label": _("Total Hours"),
				"fieldname": "total_hours",
				"fieldtype": "Float",
				"width": 120,
			},
		]

	return [
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Member"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "LANDA Member",
			"width": 120,
		},
		{
			"label": _("Member Name"),
			"fieldname": "member_name",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Activity Title"),
			"fieldname": "title",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Planned Duration (Hours)"),
			"fieldname": "planned_duration",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Duration (Hours)"),
			"fieldname": "duration",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Water Body"),
			"fieldname": "water_body",
			"fieldtype": "Link",
			"options": "Water Body",
			"width": 150,
		},
		{
			"label": _("Location"),
			"fieldname": "location",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 200,
		},
	]


def get_data(filters):
	conditions = get_conditions(filters)

	if filters.get("group_by_member"):
		return frappe.db.sql(
			f"""
			SELECT
				wam.member,
				wam.member_name,
				SUM(wam.duration) as total_hours
			FROM `tabWork Assignment Member` wam
			JOIN `tabWork Assignment` wa ON wam.parent = wa.name
			WHERE 1=1 {conditions}
			GROUP BY wam.member
			ORDER BY total_hours DESC
			""",
			filters,
			as_dict=True,
		)

	return frappe.db.sql(
		f"""
		SELECT
			wa.date,
			wam.member,
			wam.member_name,
			wa.title,
			wa.planned_duration,
			wam.duration,
			wa.water_body,
			wa.location,
			wa.description
		FROM `tabWork Assignment Member` wam
		JOIN `tabWork Assignment` wa ON wam.parent = wa.name
		WHERE 1=1 {conditions}
		ORDER BY wa.date DESC, wam.member
		""",
		filters,
		as_dict=True,
	)


def get_conditions(filters):
	conditions = []

	if filters.get("year"):
		conditions.append("AND YEAR(wa.date) = %(year)s")

	if filters.get("organization"):
		conditions.append("AND wa.organization = %(organization)s")

	if filters.get("member"):
		conditions.append("AND wam.member = %(member)s")

	if filters.get("water_body"):
		conditions.append("AND wa.water_body = %(water_body)s")

	return " ".join(conditions)
