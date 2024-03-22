# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import Optional

import frappe
from pypika.functions import Sum

from landa.water_body_management.report.catch_log_statistics.catch_log_statistics import (
	add_or_filters,
)


def get_columns():
	return [
		{
			"fieldname": "year",
			"fieldtype": "Data",
			"label": "Year",
		},
		{
			"fieldname": "water_body",
			"fieldtype": "Link",
			"label": "Water Body",
			"options": "Water Body",
		},
		{
			"fieldname": "water_body_title",
			"fieldtype": "Data",
			"label": "Water Body Title",
			"width": 200,
		},
		{
			"fieldname": "fishing_days",
			"fieldtype": "Int",
			"label": "Fishing Days",
		},
	]


def get_data(
	year: Optional[int] = None,
	water_bodies: Optional[list] = None,
	organization: Optional[str] = None,
	fishing_areas: Optional[list] = None,
	origin_of_catch_log_entry: Optional[str] = None,
):
	entry = frappe.qb.DocType("Catch Log Entry")

	query = (
		frappe.qb.from_(entry)
		.select(
			entry.year,
			entry.water_body,
			entry.water_body_title,
			Sum(entry.fishing_days),
		)
		.where(entry.workflow_state == "Approved")
		.groupby(
			entry.year,
			entry.water_body,
			entry.water_body_title,
		)
	)

	if year:
		query = query.where(entry.year == year)

	if water_bodies:
		query = query.where(entry.water_body.isin(water_bodies))

	if organization:
		query = query.where(entry.organization == organization)

	if fishing_areas:
		query = query.where(entry.fishing_area.isin(fishing_areas))

	if origin_of_catch_log_entry:
		query = query.where(entry.origin_of_catch_log_entry == origin_of_catch_log_entry)

	query = add_or_filters(query, entry)

	return query.run()


def execute(filters=None):
	year = filters.pop("year", None)
	water_bodies = filters.pop("water_body", [])
	organization = filters.pop("organization", None)
	fishing_areas = filters.pop("fishing_area", [])
	origin_of_catch_log_entry = filters.pop("origin_of_catch_log_entry", None)

	return get_columns(), get_data(
		year, water_bodies, organization, fishing_areas, origin_of_catch_log_entry
	)
