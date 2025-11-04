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
	show_share_of_avl: bool = False,
	show_share_of_avs: bool = False,
	show_share_of_ave: bool = False,
	show_area_name: bool = False,
	show_water_body_size: bool = False,
	show_water_body_status: bool = False,
	group_by_fish_species: bool = False,
):
	columns = []

	if not group_by_fish_species:
		columns.extend(
			[
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
		)

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
			}
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

	columns.extend(
		[
			{
				"fieldname": "fish_species",
				"fieldtype": "Link",
				"label": _("Fish Species"),
				"options": "Fish Species",
				"width": 150,
			},
			{
				"fieldname": "amount",
				"fieldtype": "Int",
				"label": _("Number of Fish"),
				"width": 150,
			},
			{
				"fieldname": "weight_in_kg",
				"fieldtype": "Float",
				"label": _("Weight in Kg"),
				"width": 150,
				"precision": 2,
			},
		]
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
	show_share_of_avl: bool = False,
	show_share_of_avs: bool = False,
	show_share_of_ave: bool = False,
	show_area_name: bool = False,
	show_water_body_size: bool = False,
	show_water_body_status: bool = False,
	group_by_fish_species: bool = False,
):
	entry = frappe.qb.DocType("Catch Log Entry")
	child_table = frappe.qb.DocType("Catch Log Fish Table")
	water_body = frappe.qb.DocType("Water Body")
	qb_filters = get_qb_filters(filters, entry, child_table)

	query = (
		frappe.qb.from_(entry)
		.select(
			child_table.fish_species,
			Sum(child_table.amount).as_("amount"),
			Sum(child_table.weight_in_kg).as_("weight_in_kg"),
		)
		.left_join(water_body)
		.on(entry.water_body == water_body.name)
		.join(child_table)
		.on(entry.name == child_table.parent)
	)
	group_by_fields = [
		child_table.fish_species,
	]

	if not group_by_fish_species:
		query = query.select(
			entry.water_body,
			water_body.title.as_("water_body_title"),
		)
		group_by_fields.extend(
			[
				entry.water_body,
				water_body.title,
			]
		)

	if show_water_body_status:
		query = query.select(water_body.status.as_("water_body_status"))
		group_by_fields.append(water_body.status)

	if show_area_name:
		area = frappe.qb.DocType("Fishing Area")
		query = query.left_join(area).on(entry.fishing_area == area.name).select(area.area_name)
		group_by_fields.append(area.area_name)

	if show_water_body_size:
		query = query.select(water_body.water_body_size, water_body.water_body_size_unit)
		group_by_fields.extend(
			[
				water_body.water_body_size,
				water_body.water_body_size_unit,
			]
		)

	if is_regional_or_state_employee():
		for show, regional_org, column_name in (
			(show_share_of_avl, "AVL", "share_of_avl"),
			(show_share_of_avs, "AVS", "share_of_avs"),
			(show_share_of_ave, "AVE", "share_of_ave"),
		):
			if not show:
				continue

			by_all_regional_orgs = get_subquery(entry, child_table, qb_filters)
			by_regional_org = get_subquery(
				entry,
				child_table,
				qb_filters + [Substring(entry.organization, 1, 3) == regional_org],  # index starts at 1
			)

			proportion_regional = (
				frappe.qb.from_(by_all_regional_orgs)
				.left_join(by_regional_org)
				.on(
					(by_all_regional_orgs.water_body == by_regional_org.water_body)
					& (by_all_regional_orgs.fish_species == by_regional_org.fish_species)
				)
				.select(
					by_all_regional_orgs.water_body,
					by_all_regional_orgs.fish_species,
					(
						Coalesce(by_regional_org.total_weight_in_kg, 0)
						/ by_all_regional_orgs.total_weight_in_kg
						* 100
					).as_(column_name),
				)
			)
			query = (
				query.left_join(proportion_regional)
				.on(
					(entry.water_body == proportion_regional.water_body)
					& (child_table.fish_species == proportion_regional.fish_species)
				)
				.select(proportion_regional[column_name])
			)

	query = filter_and_group(query, entry, qb_filters, group_by_fields=group_by_fields)
	return query.run(as_dict=True)


def get_subquery(entry: "Table", child_table: "Table", qb_filters: "List[Criterion]"):
	subquery = (
		frappe.qb.from_(entry)
		.join(child_table)
		.on(entry.name == child_table.parent)
		.select(
			entry.water_body,
			child_table.fish_species,
			Sum(child_table.weight_in_kg).as_("total_weight_in_kg"),
		)
	)

	return filter_and_group(
		subquery,
		entry,
		qb_filters,
		group_by_fields=[entry.water_body, child_table.fish_species],
	)


def filter_and_group(
	query,
	entry: "Table",
	qb_filters: "List[Criterion]",
	group_by_fields=None,
):
	query = add_conditions(query, qb_filters)
	query = add_or_filters(query, entry)

	if group_by_fields:
		query = query.groupby(*group_by_fields)

	return query


def get_qb_filters(filters, entry, child_table):
	filters["workflow_state"] = "Approved"
	fish_species = filters.pop("fish_species", [])
	water_body = filters.pop("water_body", [])
	fishing_area = filters.pop("fishing_area", [])
	from_year = filters.pop("from_year", None)
	to_year = filters.pop("to_year", None)

	qb_filters = [entry[key] == value for key, value in filters.items()]

	if fish_species:
		qb_filters.append(child_table.fish_species.isin(fish_species))

	if water_body:
		qb_filters.append(entry.water_body.isin(water_body))

	if fishing_area:
		qb_filters.append(entry.fishing_area.isin(fishing_area))

	if from_year:
		qb_filters.append(entry.year >= from_year)

	if to_year:
		qb_filters.append(entry.year <= to_year)

	return qb_filters


def execute(filters=None):
	group_by_fish_species = bool(filters.pop("group_by_fish_species", 0))
	extra_columns = filters.pop("extra_columns", [])

	if not group_by_fish_species:
		show_share_of_avl = "share_of_avl" in extra_columns
		show_share_of_avs = "share_of_avs" in extra_columns
		show_share_of_ave = "share_of_ave" in extra_columns
		show_area_name = "area_name" in extra_columns
		show_water_body_size = "water_body_size" in extra_columns
		show_water_body_status = "water_body_status" in extra_columns
	else:
		show_share_of_avl = False
		show_share_of_avs = False
		show_share_of_ave = False
		show_area_name = False
		show_water_body_size = False
		show_water_body_status = False

	return (
		get_columns(
			show_share_of_avl,
			show_share_of_avs,
			show_share_of_ave,
			show_area_name,
			show_water_body_size,
			show_water_body_status,
			group_by_fish_species,
		),
		get_data(
			filters,
			show_share_of_avl,
			show_share_of_avs,
			show_share_of_ave,
			show_area_name,
			show_water_body_size,
			show_water_body_status,
			group_by_fish_species,
		)
		or [],
	)
