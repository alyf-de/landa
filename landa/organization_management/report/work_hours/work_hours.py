# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


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
	filters = filters or {}
	assignment_filters = get_assignment_filters(filters)
	member_filters = {}

	if filters.get("member"):
		member_filters["member"] = filters.get("member")

	assignments_by_name = {}
	if assignment_filters:
		assignments_list = frappe.get_list(
			"Work Assignment",
			filters=assignment_filters,
			fields=[
				"name",
				"date",
				"title",
				"planned_duration",
				"water_body",
				"location",
				"description",
			],
			limit_page_length=0,
		)
		if not assignments_list:
			return []

		assignments_by_name = {a["name"]: a for a in assignments_list}
		member_filters["parent"] = ("in", list(assignments_by_name.keys()))

	members = frappe.get_list(
		"Work Assignment Member",
		filters=member_filters,
		fields=["parent", "member", "member_name", "duration"],
		parent_doctype="Work Assignment",
		limit_page_length=0,
	)

	if not members:
		return []

	if filters.get("group_by_member"):
		totals = {}
		for row in members:
			member = row.get("member")
			entry = totals.get(member)
			if entry is None:
				totals[member] = {
					"member": member,
					"member_name": row.get("member_name"),
					"total_hours": float(row.get("duration") or 0),
				}
				continue

			entry["total_hours"] += float(row.get("duration") or 0)
			if not entry.get("member_name") and row.get("member_name"):
				entry["member_name"] = row.get("member_name")

		return sorted(totals.values(), key=lambda row: row["total_hours"], reverse=True)

	if not assignments_by_name:
		parent_names = list({row.get("parent") for row in members if row.get("parent")})
		if parent_names:
			assignments_list = frappe.get_list(
				"Work Assignment",
				filters={"name": ("in", parent_names)},
				fields=[
					"name",
					"date",
					"title",
					"planned_duration",
					"water_body",
					"location",
					"description",
				],
				limit_page_length=0,
			)
			assignments_by_name = {a["name"]: a for a in assignments_list}

	data = []
	for row in members:
		assignment = assignments_by_name.get(row.get("parent"))
		if not assignment:
			continue

		data.append(
			{
				"date": assignment.get("date"),
				"member": row.get("member"),
				"member_name": row.get("member_name"),
				"title": assignment.get("title"),
				"planned_duration": assignment.get("planned_duration"),
				"duration": row.get("duration"),
				"water_body": assignment.get("water_body"),
				"location": assignment.get("location"),
				"description": assignment.get("description"),
			}
		)

	default_date = getdate("1900-01-01")
	data.sort(key=lambda row: (row.get("member") or ""))
	data.sort(key=lambda row: row.get("date") or default_date, reverse=True)
	return data


def get_assignment_filters(filters):
	assignment_filters = {}

	if filters.get("year"):
		year = int(filters.get("year"))
		assignment_filters["date"] = ["between", [f"{year}-01-01", f"{year}-12-31"]]

	if filters.get("organization"):
		assignment_filters["organization"] = filters.get("organization")

	if filters.get("water_body"):
		assignment_filters["water_body"] = filters.get("water_body")

	return assignment_filters
