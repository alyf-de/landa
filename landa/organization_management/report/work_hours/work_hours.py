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
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{
			"label": _("Member"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "LANDA Member",
			"width": 120,
		},
		{"label": _("Member Name"), "fieldname": "member_name", "fieldtype": "Data", "width": 150},
		{"label": _("Activity Title"), "fieldname": "title", "fieldtype": "Data", "width": 200},
		{
			"label": _("Planned Duration (Hours)"),
			"fieldname": "planned_duration",
			"fieldtype": "Float",
			"width": 120,
		},
		{"label": _("Duration (Hours)"), "fieldname": "duration", "fieldtype": "Float", "width": 120},
		{
			"label": _("Water Body"),
			"fieldname": "water_body",
			"fieldtype": "Link",
			"options": "Water Body",
			"width": 150,
		},
		{"label": _("Location"), "fieldname": "location", "fieldtype": "Data", "width": 150},
		{"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 200},
	]


def get_data(filters):
	filters = filters or {}
	ledger_filters = _get_ledger_filters(filters)

	if filters.get("group_by_member"):
		return frappe.get_list(
			"Work Ledger Entry",
			filters=ledger_filters,
			fields=[
				"member",
				"member_name",
				"sum(hours_change) as total_hours",
			],
			group_by="member, member_name",
			order_by="total_hours desc",
		)

	entries = frappe.get_list(
		"Work Ledger Entry",
		filters=ledger_filters,
		fields=["date", "member", "member_name", "work_assignment", "hours_change"],
		order_by="date desc",
	)

	if not entries:
		return []

	assignment_names = list({e.get("work_assignment") for e in entries if e.get("work_assignment")})
	assignments_by_name = {}
	if assignment_names:
		for a in frappe.get_list(
			"Work Assignment",
			filters={"name": ("in", assignment_names)},
			fields=["name", "title", "planned_duration", "water_body", "location", "description"],
		):
			assignments_by_name[a["name"]] = a

	data = []
	for row in entries:
		assignment = assignments_by_name.get(row.get("work_assignment")) or {}
		data.append(
			{
				"date": row.get("date"),
				"member": row.get("member"),
				"member_name": row.get("member_name"),
				"title": assignment.get("title"),
				"planned_duration": assignment.get("planned_duration"),
				"duration": row.get("hours_change"),
				"water_body": assignment.get("water_body"),
				"location": assignment.get("location"),
				"description": assignment.get("description"),
			}
		)

	default_date = getdate("1900-01-01")
	data.sort(key=lambda r: (r.get("member") or ""))
	data.sort(key=lambda r: r.get("date") or default_date, reverse=True)
	return data


def _get_ledger_filters(filters):
	ledger_filters = {}

	if filters.get("year"):
		year = int(filters["year"])
		ledger_filters["date"] = ["between", [f"{year}-01-01", f"{year}-12-31"]]

	if filters.get("organization"):
		ledger_filters["organization"] = filters["organization"]

	if filters.get("member"):
		ledger_filters["member"] = filters["member"]

	if filters.get("water_body"):
		assignment_names = frappe.get_list(
			"Work Assignment",
			filters={"water_body": filters["water_body"]},
			pluck="name",
		)
		if not assignment_names:
			return {"name": "__no_match__"}
		ledger_filters["work_assignment"] = ("in", assignment_names)

	return ledger_filters
