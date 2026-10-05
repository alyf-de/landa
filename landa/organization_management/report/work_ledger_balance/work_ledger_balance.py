# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	return columns, data


def get_columns():
	return [
		{
			"label": _("Member"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "LANDA Member",
			"width": 150,
		},
		{"label": _("Member Name"), "fieldname": "member_name", "fieldtype": "Data", "width": 180},
		{
			"label": _("Balance End Previous Year"),
			"fieldname": "balance_previous_year",
			"fieldtype": "Float",
			"width": 200,
		},
		{
			"label": _("Expected This Year"),
			"fieldname": "expected_this_year",
			"fieldtype": "Float",
			"width": 200,
		},
		{
			"label": _("Worked This Year"),
			"fieldname": "worked_this_year",
			"fieldtype": "Float",
			"width": 200,
		},
		{
			"label": _("Balance End of Year"),
			"fieldname": "balance_end_of_year",
			"fieldtype": "Float",
			"width": 200,
		},
	]


def get_data(filters):
	year = int(filters.get("year") or frappe.utils.getdate().year)
	year_start = getdate(f"{year}-01-01")
	year_end = getdate(f"{year}-12-31")

	org_filter = filters.get("organization")
	member_filter = filters.get("member")

	base_filters = [["date", "<=", year_end]]
	if org_filter:
		base_filters.append(["organization", "=", org_filter])
	if member_filter:
		base_filters.append(["member", "=", member_filter])

	entries = frappe.get_list(
		"Work Ledger Entry",
		filters=base_filters,
		fields=["member", "member_name", "date", "hours_change", "is_system_generated"],
	)
	if not entries:
		return []

	by_member = {}
	for row in entries:
		m = row["member"]
		if m not in by_member:
			by_member[m] = {"member": m, "member_name": row.get("member_name"), "rows": []}
		by_member[m]["rows"].append(
			{
				"date": row["date"],
				"hours_change": float(row.get("hours_change") or 0),
				"is_system_generated": row.get("is_system_generated"),
			}
		)

	result = []
	for member, data in by_member.items():
		balance_previous = sum(
			r["hours_change"] for r in data["rows"] if r["date"] is not None and r["date"] < year_start
		)
		in_year = [
			row for row in data["rows"] if row["date"] is not None and year_start <= row["date"] <= year_end
		]
		obligation = sum(row["hours_change"] for row in in_year if row.get("is_system_generated"))
		worked_this_year = sum(row["hours_change"] for row in in_year if not row.get("is_system_generated"))
		expected_this_year = -obligation
		balance_end = balance_previous - expected_this_year + worked_this_year

		result.append(
			{
				"member": member,
				"member_name": data["member_name"],
				"balance_previous_year": round(balance_previous, 2),
				"expected_this_year": round(expected_this_year, 2),
				"worked_this_year": round(worked_this_year, 2),
				"balance_end_of_year": round(balance_end, 2),
			}
		)

	result.sort(key=lambda r: (r["member_name"] or "", r["member"]))
	return result
