# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import List

import frappe
from frappe import _
from pypika.functions import Coalesce, Substring, Sum
from pypika.queries import Table
from pypika.terms import Criterion

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
		"fieldname": "fishing_area",
		"fieldtype": "Link",
		"label": "Fishing Area",
		"options": "Fishing Area",
	},
	{
		"fieldname": "fishing_days",
		"fieldtype": "Int",
		"label": "Fishing Days",
	},
	{  # displayed only for regional or state employees
		"fieldname": "by_foreign_regional_org",
		"fieldtype": "Percent",
		"label": _("Share of other Regional Organizations"),
	},
]


def get_data(filters):
	filters["workflow_state"] = "Approved"
	from_year = filters.pop("from_year", None)
	to_year = filters.pop("to_year", None)

	entry = frappe.qb.DocType("Catch Log Entry")
	qb_filters = get_qb_filters(filters, entry)

	if from_year:
		qb_filters.append(entry.year >= from_year)

	if to_year:
		qb_filters.append(entry.year <= to_year)

	by_all_regional_orgs = get_subquery(entry, qb_filters)
	by_foreign_regional_orgs = get_subquery(
		entry,
		qb_filters + [Substring(entry.organization, 1, 3) != entry.regional_organization],
		# index starts at 1
	)

	proportion_foreign = (
		frappe.qb.from_(by_all_regional_orgs)
		.left_join(by_foreign_regional_orgs)
		.on(by_all_regional_orgs.water_body == by_foreign_regional_orgs.water_body)
		.select(
			by_all_regional_orgs.water_body,
			(
				Coalesce(by_foreign_regional_orgs.total_fishing_days, 0)
				/ by_all_regional_orgs.total_fishing_days
				* 100
			).as_("by_foreign_regional_org"),
		)
	)

	query = (
		frappe.qb.from_(entry)
		.left_join(proportion_foreign)
		.on(entry.water_body == proportion_foreign.water_body)
		.select(
			entry.year,
			entry.water_body,
			entry.fishing_area,
			Sum(entry.fishing_days),
		)
	)

	if is_regional_or_state_employee():
		query = query.select(proportion_foreign.by_foreign_regional_org)

	query = filter_and_group(query, entry, qb_filters)

	columns = [col["fieldname"] for col in COLUMNS]
	if is_regional_or_state_employee():
		columns.append("by_foreign_regional_org")

	def tuple_to_dict(tup, columns):
		return {columns[i]: tup[i] for i in range(len(tup))}

	data = [tuple_to_dict(row, columns) for row in query.run()]

	def postprocess(row):
		row["year"] = str(row.get("year"))  # avoid year getting summed up
		return list(row.values())

	return [postprocess(row) for row in data]


def get_qb_filters(
	filters,
	entry,
):
	filters["workflow_state"] = "Approved"
	fish_species = filters.pop("fish_species", None)
	from_year = filters.pop("from_year", None)
	to_year = filters.pop("to_year", None)

	qb_filters = [entry[key] == value for key, value in filters.items()]

	if from_year:
		qb_filters.append(entry.year >= from_year)

	if to_year:
		qb_filters.append(entry.year <= to_year)

	return qb_filters


def add_conditions(query, conditions):
	for condition in conditions:
		query = query.where(condition)

	return query


def get_user_roles():
	return set(frappe.get_roles())


def add_or_filters(query, entry):
	"""Return a dict of filters that restricts the results to what the user is
	allowed to see.

	STATE_ROLES		no filters
	REGIONAL_ROLES	everything related to their water bodys OR to their member organizations
	LOCAL_ROLES		everything related to their own organization and OR to the water bodys it is supporting
	"""
	user_roles = get_user_roles()

	if user_roles.intersection(STATE_ROLES):
		return query

	# User is not a state organization employee

	member_data = get_current_member_data()
	if not member_data:
		frappe.throw(_("You are not a member of any organization."))

	if user_roles.intersection(REGIONAL_ROLES):
		return query.where(
			(entry.regional_organization == member_data.regional_organization)
			| entry.organization.like(f"{member_data.regional_organization}-%")
		)

	# User is not in regional organization management
	supported_water_bodies = get_supported_water_bodies(member_data.local_organization)
	if supported_water_bodies:
		return query.where(
			entry.organization.like(f"{member_data.local_organization}%")
			| entry.water_body.isin(supported_water_bodies)
		)

	return query.where(entry.organization.like(f"{member_data.local_organization}%"))


def filter_and_group(query, entry: Table, qb_filters: List[Criterion]):
	query = add_conditions(query, qb_filters)
	query = add_or_filters(query, entry)
	return query


def get_subquery(entry: Table, qb_filters: List[Criterion]):
	subquery = frappe.qb.from_(entry).select(
		entry.water_body,
		Sum(entry.fishing_days).as_("total_fishing_days"),
	)

	return filter_and_group(subquery, entry, qb_filters)


def is_regional_or_state_employee():
	user_roles = get_user_roles()
	return REGIONAL_ROLES.intersection(user_roles) or STATE_ROLES.intersection(user_roles)


def execute(filters=None):
	return COLUMNS, get_data(filters)


def get_or_filters():
	"""Return a dict of filters that restricts the results to what the user is
	allowed to see.
	STATE_ROLES		no filters
	REGIONAL_ROLES	everything related to their water bodys OR to their member organizations
	LOCAL_ROLES		everything related to their own organization and OR to the water bodys it is supporting
	"""
	or_filters = {}
	user_roles = set(frappe.get_roles())

	if user_roles.intersection(STATE_ROLES):
		return or_filters

	# User is nota state organization employee
	member_data = get_current_member_data()
	if not member_data:
		frappe.throw(_("You are not a member of any organization."))

	if user_roles.intersection(REGIONAL_ROLES):
		or_filters["regional_organization"] = member_data.regional_organization
		or_filters["organization"] = ("like", f"{member_data.regional_organization}-%")
	else:
		# User is not in regional organization management
		or_filters["water_body"] = (
			"in",
			get_supported_water_bodies(member_data.local_organization),
		)
		or_filters["organization"] = member_data.local_organization

	return or_filters
