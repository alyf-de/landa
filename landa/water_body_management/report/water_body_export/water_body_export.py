# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": _("Name"),
			"fieldtype": "Link",
			"options": "Water Body",
			"width": 100,
		},
		{
			"fieldname": "title",
			"label": _("Titel"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "fishing_area_name",
			"label": _("Fishing Area Name"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "water_body_size",
			"label": _("Water Body Size"),
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "water_body_size_unit",
			"label": _("Water Body Size Unit"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "is_active",
			"label": _("Is Active"),
			"fieldtype": "Check",
			"width": 50,
		},
		{
			"fieldname": "has_master_key_system",
			"label": _("Has Master Key System"),
			"fieldtype": "Check",
			"width": 50,
		},
		{
			"fieldname": "guest_passes_available",
			"label": _("Guest Passes Available"),
			"fieldtype": "Check",
			"width": 50,
		},
		{
			"fieldname": "general_public_information",
			"label": _("General Public Information"),
			"fieldtype": "Small Text",
			"width": 100,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "fish_species_short_codes",
			"label": _("Fish Species Short Codes"),
			"fieldtype": "Small Text",
			"width": 100,
		},
		{
			"fieldname": "fish_species",
			"label": _("Fish Species"),
			"fieldtype": "Small Text",
			"width": 100,
		},
		{
			"fieldname": "special_provisions",
			"label": _("Water Body Special Provisions"),
			"fieldtype": "Small Text",
			"width": 100,
		},
	]


def execute(filters=None):
	return get_columns(), get_data()


def get_data():
	return tuple(
		(*wb, *get_data_from_child_tables(wb[0]))
		for wb in frappe.get_all(
			"Water Body",
			fields=[
				"name",
				"title",
				"fishing_area_name",
				"water_body_size",
				"water_body_size_unit",
				"is_active",
				"has_master_key_system",
				"guest_passes_available",
				"general_public_information",
				"status",
			],
			as_list=True,
		)
	)


def get_data_from_child_tables(water_body: str):
	fish_species = frappe.get_all(
		"Fish Species Table",
		filters={"parent": water_body, "parenttype": "Water Body"},
		fields=["fish_species", "short_code"],
	)
	special_provisions = frappe.get_all(
		"Water Body Special Provision Table",
		filters={"parent": water_body, "parenttype": "Water Body"},
		pluck="water_body_special_provision",
	)
	short_codes = ", ".join(fs.short_code for fs in fish_species if fs.short_code)
	species = ", ".join(fs.fish_species for fs in fish_species if fs.fish_species)
	provisions = ", ".join(sp for sp in special_provisions if sp)

	return short_codes, species, provisions
