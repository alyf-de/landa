# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

from datetime import datetime
from typing import Optional

import frappe
from frappe import _

from landa.utils import get_current_member_data


def execute(filters):
	organization = filters.pop("organization", None)
	year_of_settlement = filters.pop("year_of_settlement", None)

	if organization and not isinstance(organization, str):
		frappe.throw(_("Invalid organization"))

	if year_of_settlement and not isinstance(year_of_settlement, int):
		frappe.throw(_("Invalid year of settlement"))

	return get_columns(), list(get_data(organization, year_of_settlement))


def get_columns():
	return [
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"options": "Organization",
			"label": _("Organization"),
			"width": 200,
		},
		{
			"fieldname": "year_of_settlement",
			"fieldtype": "Data",
			"label": _("Year of Settlement"),
			"disable_total": True,
			"width": 200,
		},
		{
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"label": _("Outstanding Amount"),
			"width": 200,
		},
	]


def get_data(organization: Optional[str] = None, year_of_settlement: Optional[int] = None):
	years_of_settlement = (
		[year_of_settlement] if year_of_settlement else list(range(2021, datetime.now().year + 1))
	)

	if organization:
		organizations = [organization]
	else:
		org_filters = []
		member_data = get_current_member_data()
		if member_data.regional_organization:
			org_filters.append(["parent_organization", "=", member_data.regional_organization])

		organizations = frappe.get_list("Organization", filters=org_filters, pluck="name")

	for year in years_of_settlement:
		for org in organizations:
			invoiced_amount = frappe.get_list(
				"Sales Invoice",
				fields=["sum(base_grand_total)"],
				filters={
					"docstatus": 1,
					"year_of_settlement": year,
					"organization": org,
				},
				as_list=True,
			)
			invoiced_amount = invoiced_amount[0][0] or 0.0

			received_amount = frappe.get_list(
				"Payment Entry",
				fields=["sum(base_received_amount)"],
				filters={
					"docstatus": 1,
					"year_of_settlement": year,
					"organization": org,
					"payment_type": "Receive",
				},
				as_list=True,
			)
			received_amount = received_amount[0][0] or 0.0

			paid_amount = frappe.get_list(
				"Payment Entry",
				fields=["sum(base_paid_amount)"],
				filters={
					"docstatus": 1,
					"year_of_settlement": year,
					"organization": org,
					"payment_type": "Pay",
				},
				as_list=True,
			)
			paid_amount = paid_amount[0][0] or 0.0

			yield (
				org,
				year,
				invoiced_amount - received_amount + paid_amount,
			)
