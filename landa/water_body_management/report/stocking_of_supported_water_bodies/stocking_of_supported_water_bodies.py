# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe

from landa.water_body_management.report.catch_log_statistics.catch_log_statistics import (
	get_supported_water_bodies,
	get_member_name_and_local_organization,
)


COLUMNS = [
	{
		"fieldname": "date",
		"fieldtype": "Date",
		"label": "Date",
	},
	{
		"fieldname": "year",
		"fieldtype": "Select",
		"label": "Year",
		"options": "2022\n2023\n2024\n2025\n2026\n2027\n2028\n2029",
	},
	# {
	#	"fieldname": "fishing_area",
	#	"fieldtype": "Link",
	#	"label": "Fishing Area",
	#	"options": "Fishing Area",
	# },
	{
		"fieldname": "water_body",
		"fieldtype": "Link",
		"label": "Water Body",
		"options": "Water Body",
	},
	{
		"fieldname": "fish_species",
		"fieldtype": "Link",
		"label": "Fish Species",
		"options": "Fish Species",
	},
	{
		"fieldname": "fish_type_for_stocking",
		"fieldtype": "Link",
		"label": "Fish Type For Stocking",
		"options": "Fish Type For Stocking",
	},
	{"fieldname": "weight", "fieldtype": "Float", "label": "Weight in Kg", "reqd": 1},
	{"fieldname": "quantity", "fieldtype": "Float", "label": "Quantity"},
	# {
	#	"fieldname": "price_per_kilogram",
	#	"fieldtype": "Float",
	#	"label": "Price per Kilogram",
	#	"options": "currency",
	# },
	# {
	#	"fieldname": "price_for_total_weight",
	#	"fieldtype": "Float",
	#	"label": "Price for Total Weight",
	#	"options": "currency",
	# },
	# {
	#	"default": "EUR",
	#	"fieldname": "currency",
	#	"fieldtype": "Link",
	#	"label": "Currency",
	#	"options": "Currency",
	# },
	# {
	#	"fieldname": "organization",
	#	"fieldtype": "Data",
	#	"label": "Organization",
	#	"options": "Organization",
	# },
	{
		"fieldname": "weight_per_water_body_size",
		"fieldtype": "Float",
		"label": "Weight per Water Body Size",
	},
	{
		"fieldname": "unit_of_weight_per_water_body_size",
		"fieldtype": "Data",
		"label": "Unit of Weight per Water Body Size",
	},
	{
		"fieldname": "quantity_per_water_body_size",
		"fieldtype": "Float",
		"label": "Quantity per Water Body Size",
	},
	{
		"fieldname": "unit_of_quantity_per_water_body_size",
		"fieldtype": "Data",
		"label": "Unit of Quantity per Water Body Size",
	},
	{
		"fieldname": "water_body_size",
		"fieldtype": "Float",
		"label": "Water Body Size",
	},
	{
		"fieldname": "water_body_size_unit",
		"fieldtype": "Data",
		"label": "Water Body Size Unit",
	},
	# {
	#	"fieldname": "supplier",
	#	"fieldtype": "Link",
	#	"label": "Supplier",
	#	"options": "External Contact",
	# },
	# {
	#	"fieldname": "full_name_of_supplier",
	#	"fieldtype": "Data",
	#	"label": "Full Name of Supplier",
	# },
	# {
	#	"fieldname": "company_of_supplier",
	#	"fieldtype": "Data",
	#	"label": "Company of Supplier",
	# },
	{
		"fieldname": "stocking_target",
		"fieldtype": "Link",
		"label": "Stocking Target",
		"options": "Stocking Target",
	},
]


def get_data(filters):
	filters["status"] = "Completed"
	or_filters = {}
	local_organization = get_member_name_and_local_organization()[1]
	if local_organization:
		or_filters["water_body"] = ("in", get_supported_water_bodies(local_organization))

	data = frappe.get_all(
		"Stocking Measure",
		fields=[column.get("fieldname") for column in COLUMNS],
		filters=filters,
		or_filters=or_filters,
	)

	return data


def execute(filters=None):
	return COLUMNS, get_data(filters)
