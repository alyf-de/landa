# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import List, Optional

import frappe
from frappe import _
from pypika.functions import Sum

from landa.water_body_management.report.catch_log_statistics.catch_log_statistics import (
	add_or_filters,
)


def get_columns(extra_columns: List[str]) -> List[dict]:
	columns = [
		{
			"fieldname": "year",
			"fieldtype": "Data",
			"label": _("Year"),
		},
		{
			"fieldname": "water_body",
			"fieldtype": "Link",
			"label": _("Water Body"),
			"options": "Water Body",
		},
		{
			"fieldname": "water_body_title",
			"fieldtype": "Data",
			"label": _("Water Body Title"),
			"width": 200,
		},
	]

	if "water_body_status" in extra_columns:
		columns.append(
			{
				"fieldname": "water_body_status",
				"fieldtype": "Data",
				"label": _("Status"),
				"width": 150,
			}
		)

	if "area_name" in extra_columns:
		columns.append(
			{
				"fieldname": "area_name",
				"fieldtype": "Data",
				"label": _("Area Name"),
			},
		)

	if "water_body_size" in extra_columns:
		columns.extend(
			[
				{
					"fieldname": "water_body_size",
					"fieldtype": "Float",
					"label": _("Water Body Size"),
					"precision": "2",
				},
				{
					"fieldname": "water_body_size_unit",
					"fieldtype": "Data",
					"label": _("Unit"),
					"width": 80,
				},
			]
		)

	columns.append(
		{
			"fieldname": "fishing_days",
			"fieldtype": "Int",
			"label": _("Fishing Days"),
		},
	)

	return columns


def get_data(
	extra_columns: List[str],
	year: Optional[int] = None,
	water_bodies: Optional[List[str]] = None,
	organization: Optional[str] = None,
	fishing_areas: Optional[List[str]] = None,
	origin_of_catch_log_entry: Optional[str] = None,
):
	entry = frappe.qb.DocType("Catch Log Entry")
	water_body = frappe.qb.DocType("Water Body")

	query = (
		frappe.qb.from_(entry)
		.select(
			entry.year,
			entry.water_body,
			entry.water_body_title,
		)
		.where(entry.workflow_state == "Approved")
		.groupby(
			entry.year,
			entry.water_body,
			entry.water_body_title,
		)
	)

	if "water_body_status" in extra_columns or "water_body_size" in extra_columns:
		query = query.join(water_body).on(entry.water_body == water_body.name)

	if "water_body_status" in extra_columns:
		query = query.select(water_body.status)

	if "area_name" in extra_columns:
		area = frappe.qb.DocType("Fishing Area")
		query = query.left_join(area).on(entry.fishing_area == area.name).select(area.area_name)

	if "water_body_size" in extra_columns:
		query = query.select(water_body.water_body_size, water_body.water_body_size_unit)

	query = query.select(Sum(entry.fishing_days))

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
	extra_columns = filters.pop("extra_columns", [])

	return get_columns(extra_columns), get_data(
		extra_columns, year, water_bodies, organization, fishing_areas, origin_of_catch_log_entry
	)
