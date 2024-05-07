# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from landa.organization_management.birthday import (
	get_age,
	get_next_birthday,
	next_birthday_is_decadal,
)


def get_columns():
	return [
		{
			"fieldname": "landa_member",
			"fieldtype": "Link",
			"options": "LANDA Member",
			"label": _("Member"),
		},
		{"fieldname": "first_name", "fieldtype": "Data", "label": _("First Name")},
		{"fieldname": "last_name", "fieldtype": "Data", "label": _("Last Name")},
		{
			"fieldname": "date_of_birth",
			"fieldtype": "Date",
			"label": _("Date of Birth"),
		},
		{"fieldname": "member_age", "fieldtype": "Data", "label": _("Age")},
		{
			"fieldname": "upcoming_birthday",
			"fieldtype": "Date",
			"label": _("Upcoming Birthday"),
		},
		{
			"fieldname": "is_decadal_birthday",
			"fieldtype": "Check",
			"label": _("Is Decadal Birthday"),
		},
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"options": "Organization",
			"label": _("Organization"),
		},
		{
			"fieldname": "organization_name",
			"fieldtype": "Data",
			"label": _("Organization Name"),
		},
	]


def get_data(filters: dict):
	filters["date_of_birth"] = ("is", "set")
	member_fields = [
		"name",
		"first_name",
		"last_name",
		"date_of_birth",
		"organization",
		"organization_name",
	]
	members = frappe.get_list(
		"LANDA Member",
		filters=filters,
		fields=member_fields,
		as_list=True,
	)

	for member in members:
		idx = member_fields.index("date_of_birth")
		birthday = member[idx]
		age = get_age(birthday)

		result = list(member)
		result.insert(idx + 1, age)
		result.insert(idx + 2, get_next_birthday(birthday))
		result.insert(idx + 3, next_birthday_is_decadal(age))

		yield result


def execute(filters=None):
	return get_columns(), list(get_data(filters))
