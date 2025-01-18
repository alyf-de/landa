# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING

import frappe
from frappe import _
from pypika.functions import Sum

from landa.utils import get_current_member_data

if TYPE_CHECKING:
	from pypika.queries import QueryBuilder
	from pypika.terms import Field


def execute(filters=None):
	return get_columns(), get_data(filters.get("from_year"), filters.get("to_year"))


def get_columns():
	return [
		{
			"fieldname": "water_body",
			"label": _("Water Body"),
			"fieldtype": "Link",
			"options": "Water Body",
		},
		{
			"fieldname": "water_body_name",
			"label": _("Water Body Name"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "fish_species",
			"label": _("Fish Species"),
			"fieldtype": "Link",
			"options": "Fish Species",
			"width": 150,
		},
		{
			"fieldname": "catch_quantity",
			"label": _("Catch Quantity"),
			"fieldtype": "Int",
		},
		{
			"fieldname": "catch_weight",
			"label": _("Catch Weight"),
			"fieldtype": "Float",
		},
		{
			"fieldname": "stocking_quantity",
			"label": _("Stocking Quantity"),
			"fieldtype": "Int",
		},
		{
			"fieldname": "stocking_weight",
			"label": _("Stocking Weight"),
			"fieldtype": "Float",
		},
		{
			"fieldname": "fishing_days",
			"label": _("Fishing Days"),
			"fieldtype": "Int",
		},
	]


def get_data(from_year, to_year):
	water_body = frappe.qb.DocType("Water Body")
	fish_species = frappe.qb.DocType("Fish Species")
	stocking_measure = frappe.qb.DocType("Stocking Measure")
	catch_log = frappe.qb.DocType("Catch Log Entry")
	catch_log_fish_table = frappe.qb.DocType("Catch Log Fish Table")

	fishing_days_query = (
		frappe.qb.from_(catch_log)
		.select(catch_log.water_body, Sum(catch_log.fishing_days).as_("fishing_days"))
		.where((catch_log.year >= from_year) & (catch_log.year <= to_year))
		.groupby(catch_log.water_body)
	)

	stocking_measure_query = (
		frappe.qb.from_(stocking_measure)
		.select(
			stocking_measure.water_body,
			stocking_measure.fish_species,
			Sum(stocking_measure.quantity).as_("stocking_quantity"),
			Sum(stocking_measure.weight).as_("stocking_weight"),
		)
		.where(
			(stocking_measure.date >= f"{from_year}-01-01")
			& (stocking_measure.date <= f"{to_year}-12-31")
			& (stocking_measure.status == "Completed")
		)
		.groupby(stocking_measure.water_body, stocking_measure.fish_species)
	)

	catch_query = (
		frappe.qb.from_(catch_log)
		.left_join(catch_log_fish_table)
		.on(catch_log.name == catch_log_fish_table.parent)
		.select(
			catch_log.water_body,
			catch_log_fish_table.fish_species,
			Sum(catch_log_fish_table.amount).as_("catch_quantity"),
			Sum(catch_log_fish_table.weight_in_kg).as_("catch_weight"),
		)
		.where(
			(catch_log.year >= from_year)
			& (catch_log.year <= to_year)
			& (catch_log.workflow_state == "Approved")
		)
		.groupby(catch_log.water_body, catch_log_fish_table.fish_species)
	)

	query = (
		frappe.qb.from_(water_body)
		.cross_join(fish_species)
		.on(water_body.name == water_body.name)
		.left_join(stocking_measure_query)
		.on(
			(water_body.name == stocking_measure_query.water_body)
			& (stocking_measure_query.fish_species == fish_species.name)
		)
		.left_join(catch_query)
		.on(
			(water_body.name == catch_query.water_body) & (catch_query.fish_species == fish_species.name)
		)
		.left_join(fishing_days_query)
		.on(water_body.name == fishing_days_query.water_body)
		.select(
			water_body.name,
			water_body.title,
			fish_species.name,
			catch_query.catch_quantity,
			catch_query.catch_weight,
			stocking_measure_query.stocking_quantity,
			stocking_measure_query.stocking_weight,
			fishing_days_query.fishing_days,
		)
		.where((catch_query.catch_quantity > 0) | (stocking_measure_query.stocking_quantity > 0))
		.orderby(water_body.name, fish_species.name)
	)

	query = apply_permissions(query, regional_org_field=water_body.organization)
	results = query.run()

	if not results:
		return []

	return remove_repetitive_values(
		[list(result) for result in results],
		column_to_check=0,
		columns_to_clear=[0, 1, -1],
	)


def apply_permissions(query: "QueryBuilder", regional_org_field: "Field") -> "QueryBuilder":
	"""Ensure that the user only sees data for their own regional organization.

	Args:
	    query: query to apply permissions to.
	    regional_org_field: field to check for member's regional organization.
	"""
	member_data = get_current_member_data()
	if member_data.regional_organization:
		query = query.where(regional_org_field == member_data.regional_organization)

	return query


def remove_repetitive_values(
	results: list[list], column_to_check: int, columns_to_clear: list[int]
) -> list[list]:
	"""Remove repetitive values in a list of lists.

	Args:
	    results: list of lists, where each list represents a row.
	    column_to_check: index of the column to check for duplicates.
	    columns_to_clear: list of indices of the columns to be set to None.
	"""
	previous_value = None
	for result in results:
		current_value = result[column_to_check]
		if current_value == previous_value:
			for column_index in columns_to_clear:
				result[column_index] = None

		previous_value = current_value

	return results
