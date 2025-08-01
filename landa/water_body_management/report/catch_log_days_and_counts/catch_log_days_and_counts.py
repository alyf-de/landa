# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING, List

import frappe
from frappe import _
from pypika.functions import Sum

from landa.water_body_management.report.utils import add_conditions, add_or_filters

if TYPE_CHECKING:
	from pypika.queries import Table
	from pypika.terms import Criterion


def get_columns(
	show_area_name: bool = False,
	show_water_body_size: bool = False,
	show_water_body_status: bool = False,
) -> List[dict]:
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

	if show_water_body_status:
		columns.append(
			{
				"fieldname": "water_body_status",
				"fieldtype": "Data",
				"label": _("Status"),
				"width": 150,
			}
		)

	if show_area_name:
		columns.append(
			{
				"fieldname": "area_name",
				"fieldtype": "Data",
				"label": _("Area Name"),
			},
		)

	if show_water_body_size:
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
	filters,
	show_area_name: bool = False,
	show_water_body_size: bool = False,
	show_water_body_status: bool = False,
):
	entry = frappe.qb.DocType("Catch Log Entry")
	water_body = frappe.qb.DocType("Water Body")
	qb_filters = get_qb_filters(filters, entry)

	query = (
		frappe.qb.from_(entry)
		.select(
			entry.year,
			entry.water_body,
			entry.water_body_title,
		)
		.groupby(
			entry.year,
			entry.water_body,
			entry.water_body_title,
		)
	)

	if show_water_body_status or show_water_body_size:
		query = query.join(water_body).on(entry.water_body == water_body.name)

	if show_water_body_status:
		query = query.select(water_body.status)

	if show_area_name:
		area = frappe.qb.DocType("Fishing Area")
		query = query.left_join(area).on(entry.fishing_area == area.name).select(area.area_name)

	if show_water_body_size:
		query = query.select(water_body.water_body_size, water_body.water_body_size_unit)

	query = query.select(Sum(entry.fishing_days))

	query = filter_and_group(query, entry, qb_filters)

	return query.run()


def filter_and_group(query, entry: "Table", qb_filters: "List[Criterion]"):
	query = add_conditions(query, qb_filters)
	query = add_or_filters(query, entry)
	query = query.groupby(entry.year, entry.water_body, entry.water_body_title)

	return query


def get_qb_filters(filters, entry: "Table"):
	year = filters.pop("year", None)
	water_bodies = filters.pop("water_body", [])
	organization = filters.pop("organization", None)
	fishing_areas = filters.pop("fishing_area", [])
	origin_of_catch_log_entry = filters.pop("origin_of_catch_log_entry", None)
	qb_filters = [
		entry.workflow_state == "Approved",
	]

	if year:
		qb_filters.append(entry.year == year)

	if water_bodies:
		qb_filters.append(entry.water_body.isin(water_bodies))

	if organization:
		qb_filters.append(entry.organization == organization)

	if fishing_areas:
		qb_filters.append(entry.fishing_area.isin(fishing_areas))

	if origin_of_catch_log_entry:
		qb_filters.append(entry.origin_of_catch_log_entry == origin_of_catch_log_entry)

	return qb_filters


def execute(filters=None):
	extra_columns = filters.pop("extra_columns", [])
	show_area_name = "area_name" in extra_columns
	show_water_body_size = "water_body_size" in extra_columns
	show_water_body_status = "water_body_status" in extra_columns

	return (
		get_columns(
			show_area_name,
			show_water_body_size,
			show_water_body_status,
		),
		get_data(
			filters,
			show_area_name=show_area_name,
			show_water_body_size=show_water_body_size,
			show_water_body_status=show_water_body_status,
		),
	)
