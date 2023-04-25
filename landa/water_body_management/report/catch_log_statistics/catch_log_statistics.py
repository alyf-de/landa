# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika.functions import Sum

from landa.organization_management.doctype.organization.organization import (
	get_supported_water_bodies,
)
from landa.utils import get_current_member_data

STATE_ROLES = {"LANDA State Organization Employee", "System Manager", "Administrator"}
REGIONAL_ROLES = {
	"LANDA Regional Organization Management",
	"LANDA Regional Water Body Management",
}

COLUMNS = [
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
		"fieldname": "amount",
		"fieldtype": "Int",
		"label": "Number of Fish",
	},
	{
		"fieldname": "weight_in_kg",
		"fieldtype": "Float",
		"label": "Weight in Kg",
	},
]


def get_data(filters):
	filters["workflow_state"] = "Approved"
	fish_species = filters.pop("fish_species", None)
	from_year = filters.pop("from_year", None)
	to_year = filters.pop("to_year", None)

	entry = frappe.qb.DocType("Catch Log Entry")
	child_table = frappe.qb.DocType("Catch Log Fish Table")

	query = (
		frappe.qb.from_(entry)
		.join(child_table)
		.on(entry.name == child_table.parent)
		.select(
			entry.water_body,
			child_table.fish_species,
			Sum(child_table.amount).as_("amount"),
			Sum(child_table.weight_in_kg).as_("weight_in_kg"),
		)
	)

	for key, value in filters.items():
		query = query.where(entry[key] == value)

	if fish_species:
		query = query.where(child_table.fish_species == fish_species)

	if from_year:
		query = query.where(entry.year >= from_year)

	if to_year:
		query = query.where(entry.year <= to_year)

	query = add_or_filters(query, entry)
	query = query.groupby(entry.water_body, entry.fishing_area, child_table.fish_species)
	return query.run()


def add_or_filters(query, entry):
	"""Return a dict of filters that restricts the results to what the user is
	allowed to see.

	STATE_ROLES		no filters
	REGIONAL_ROLES	everything related to their water bodys OR to their member organizations
	LOCAL_ROLES		everything related to their own organization and OR to the water bodys it is supporting
	"""
	user_roles = set(frappe.get_roles())

	if user_roles.intersection(STATE_ROLES):
		return query

	# User is not a state organization employee

	member_data = get_current_member_data()
	if not member_data:
		frappe.throw(_("You are not a member of any organization."))

	if user_roles.intersection(REGIONAL_ROLES):
		return query.where(
			entry.regional_organization
			== member_data.regional_organization
			| entry.organization.like(f"{member_data.regional_organization}-%")
		)
	else:
		# User is not in regional organization management
		return query.where(
			entry.organization.like(f"{member_data.local_organization}%")
			| entry.water_body.isin(get_supported_water_bodies(member_data.local_organization))
		)


def execute(filters=None):
	return COLUMNS, get_data(filters) or []
