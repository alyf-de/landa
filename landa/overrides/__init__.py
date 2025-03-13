# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe
from frappe.defaults import set_user_default

from landa.utils import get_current_member_data


def set_user_defaults():
	current_member_data = get_current_member_data()
	if not current_member_data:
		return

	if not current_member_data.local_organization.endswith("000"):
		# Default organization should not be set for members of a regional organization (ending with 000)
		set_user_default("organization", current_member_data.organization)

	set_user_default("company", current_member_data.company)
	set_user_default(
		"price_list",
		frappe.db.get_value("Price List", {"company": current_member_data.company}),
	)

	# Customer is always the local organization (first seven digits of the organization)
	set_user_default("customer", current_member_data.local_organization)
