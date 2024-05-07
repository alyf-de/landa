# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe
from frappe import _

from landa.organization_management.doctype.organization.organization import (
	get_supported_water_bodies,
)
from landa.utils import get_current_member_data


def get_columns():
	return [
		{
			"fieldname": "date",
			"fieldtype": "Date",
			"label": _("Date"),
		},
		{
			"fieldname": "year",
			"fieldtype": "Select",
			"label": _("Year"),
			"options": "2022\n2023\n2024\n2025\n2026\n2027\n2028\n2029",
		},
		{
			"fieldname": "water_body",
			"fieldtype": "Link",
			"label": _("Water Body"),
			"options": "Water Body",
		},
		{
			"fieldname": "fish_species",
			"fieldtype": "Link",
			"label": _("Fish Species"),
			"options": "Fish Species",
		},
		{
			"fieldname": "fish_type_for_stocking",
			"fieldtype": "Link",
			"label": _("Fish Type For Stocking"),
			"options": "Fish Type For Stocking",
		},
		{"fieldname": "weight", "fieldtype": "Float", "label": _("Weight in Kg"), "reqd": 1},
		{"fieldname": "quantity", "fieldtype": "Float", "label": _("Quantity")},
		{
			"fieldname": "weight_per_water_body_size",
			"fieldtype": "Float",
			"label": _("Weight per Water Body Size"),
		},
		{
			"fieldname": "unit_of_weight_per_water_body_size",
			"fieldtype": "Data",
			"label": _("Unit of Weight per Water Body Size"),
		},
		{
			"fieldname": "quantity_per_water_body_size",
			"fieldtype": "Float",
			"label": _("Quantity per Water Body Size"),
		},
		{
			"fieldname": "unit_of_quantity_per_water_body_size",
			"fieldtype": "Data",
			"label": _("Unit of Quantity per Water Body Size"),
		},
		{
			"fieldname": "water_body_size",
			"fieldtype": "Float",
			"label": _("Water Body Size"),
		},
		{
			"fieldname": "water_body_size_unit",
			"fieldtype": "Data",
			"label": _("Water Body Size Unit"),
		},
		{
			"fieldname": "stocking_target",
			"fieldtype": "Link",
			"label": _("Stocking Target"),
			"options": "Stocking Target",
		},
	]


def get_data(filters):
	filters["status"] = "Completed"
	or_filters = {}
	member_data = get_current_member_data()
	if member_data:
		or_filters["water_body"] = (
			"in",
			get_supported_water_bodies(member_data.local_organization),
		)

	return frappe.get_all(
		"Stocking Measure",
		fields=[column.get("fieldname") for column in get_columns()],
		filters=filters,
		or_filters=or_filters,
	)


def execute(filters=None):
	return get_columns(), get_data(filters)
