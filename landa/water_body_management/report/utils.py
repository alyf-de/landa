from typing import TYPE_CHECKING

import frappe
from frappe import _

from landa.organization_management.doctype.organization.organization import (
	get_supported_water_bodies,
)
from landa.utils import get_current_member_data

if TYPE_CHECKING:
	from pypika.queries import Query, Table
	from pypika.terms import Criterion

STATE_ROLES = {"LANDA State Organization Employee", "System Manager", "Administrator"}
REGIONAL_ROLES = {
	"LANDA Regional Organization Management",
	"LANDA Regional Water Body Management",
}


def is_regional_or_state_employee():
	user_roles = get_user_roles()
	return REGIONAL_ROLES.intersection(user_roles) or STATE_ROLES.intersection(user_roles)


def get_user_roles() -> set[str]:
	return set(frappe.get_roles())


def add_or_filters(query: "Query", entry: "Table"):
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


def add_conditions(query: "Query", conditions: "list[Criterion]"):
	for condition in conditions:
		query = query.where(condition)

	return query
