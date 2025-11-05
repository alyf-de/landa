# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING, List

import frappe
from frappe import _
from pypika.functions import Coalesce, Substring, Sum

from landa.water_body_management.report.utils import (
	add_conditions,
	add_or_filters,
	is_regional_or_state_employee,
)

if TYPE_CHECKING:
	from pypika.queries import Table
	from pypika.terms import Criterion


def get_columns(
	show_area_name: bool = False,
	show_water_body_size: bool = False,
	show_water_body_status: bool = False,
	show_share_of_avl: bool = False,
	show_share_of_avs: bool = False,
	show_share_of_ave: bool = False,
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
			"fieldname": "total_fishing_days",
			"fieldtype": "Int",
			"label": _("Fishing Days"),
		},
	)

	if is_regional_or_state_employee():
		if show_share_of_avl:
			columns.append(
				{
					"fieldname": "share_of_avl",
					"fieldtype": "Percent",
					"label": _("Share of AVL"),
					"precision": 1,
				}
			)
		if show_share_of_avs:
			columns.append(
				{
					"fieldname": "share_of_avs",
					"fieldtype": "Percent",
					"label": _("Share of AVS"),
					"precision": 1,
				}
			)
		if show_share_of_ave:
			columns.append(
				{
					"fieldname": "share_of_ave",
					"fieldtype": "Percent",
					"label": _("Share of AVE"),
					"precision": 1,
				}
			)

	return columns


def get_data(
	filters,
	show_area_name: bool = False,
	show_water_body_size: bool = False,
	show_water_body_status: bool = False,
	show_share_of_avl: bool = False,
	show_share_of_avs: bool = False,
	show_share_of_ave: bool = False,
):
	entry = frappe.qb.DocType("Catch Log Entry")
	water_body = frappe.qb.DocType("Water Body")
	qb_filters = get_qb_filters(filters, entry)

	# Build the query without groupby initially
	query = (
		frappe.qb.from_(entry)
		.left_join(water_body)
		.on(entry.water_body == water_body.name)
		.select(
			entry.year,
			entry.water_body,
			water_body.title.as_("water_body_title"),
		)
	)

	# Track fields that need to be in GROUP BY
	group_by_fields = [
		entry.year,
		entry.water_body,
		water_body.title,
	]

	if show_water_body_status:
		query = query.select(water_body.status.as_("water_body_status"))
		group_by_fields.append(water_body.status)

	if show_area_name:
		area = frappe.qb.DocType("Fishing Area")
		query = query.left_join(area).on(entry.fishing_area == area.name).select(area.area_name)
		group_by_fields.append(area.area_name)

	if show_water_body_size:
		query = query.select(water_body.water_body_size, water_body.water_body_size_unit)
		group_by_fields.extend([water_body.water_body_size, water_body.water_body_size_unit])

	query = query.select(Sum(entry.fishing_days).as_("total_fishing_days"))

	if is_regional_or_state_employee():
		for show, regional_org, column_name in (
			(show_share_of_avl, "AVL", "share_of_avl"),
			(show_share_of_avs, "AVS", "share_of_avs"),
			(show_share_of_ave, "AVE", "share_of_ave"),
		):
			if not show:
				continue

			by_all_regional_orgs = get_subquery(entry, qb_filters)
			by_regional_org = get_subquery(
				entry,
				qb_filters + [Substring(entry.organization, 1, 3) == regional_org],  # index starts at 1
			)
			proportion_regional = (
				frappe.qb.from_(by_all_regional_orgs)
				.left_join(by_regional_org)
				.on(
					(by_all_regional_orgs.water_body == by_regional_org.water_body)
					& (by_all_regional_orgs.year == by_regional_org.year)
				)
				.select(
					by_all_regional_orgs.water_body,
					by_all_regional_orgs.year,
					(
						Coalesce(by_regional_org.total_fishing_days, 0)
						/ by_all_regional_orgs.total_fishing_days
						* 100
					).as_(column_name),
				)
			)
			query = (
				query.left_join(proportion_regional)
				.on(
					(entry.water_body == proportion_regional.water_body)
					& (entry.year == proportion_regional.year)
				)
				.select(proportion_regional[column_name])
			)
			# Note: proportion_regional columns don't need to be in GROUP BY as they come from a subquery

	query = filter_and_group(query, entry, qb_filters, group_by_fields=group_by_fields)

	return query.run(as_dict=True)


def get_subquery(entry: "Table", qb_filters: "List[Criterion]"):
	subquery = frappe.qb.from_(entry).select(
		entry.water_body,
		entry.year,
		Sum(entry.fishing_days).as_("total_fishing_days"),
	)

	# Subquery only needs to group by the fields it selects (excluding aggregates)
	return filter_and_group(
		subquery, entry, qb_filters, group_by_fields=[entry.year, entry.water_body]
	)


def filter_and_group(query, entry: "Table", qb_filters: "List[Criterion]", group_by_fields=None):
	query = add_conditions(query, qb_filters)
	query = add_or_filters(query, entry)

	if group_by_fields:
		query = query.groupby(*group_by_fields)

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
	show_share_of_avl = "share_of_avl" in extra_columns
	show_share_of_avs = "share_of_avs" in extra_columns
	show_share_of_ave = "share_of_ave" in extra_columns

	return (
		get_columns(
			show_area_name,
			show_water_body_size,
			show_water_body_status,
			show_share_of_avl,
			show_share_of_avs,
			show_share_of_ave,
		),
		get_data(
			filters,
			show_area_name,
			show_water_body_size,
			show_water_body_status,
			show_share_of_avl,
			show_share_of_avs,
			show_share_of_ave,
		),
	)
