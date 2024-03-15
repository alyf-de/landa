# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

from typing import Optional

import frappe
from frappe import _


def execute(filters=None):
	organization = filters.pop("organization", None)
	year_of_settlement = filters.pop("year_of_settlement", None)

	if not isinstance(organization, str):
		frappe.throw(_("Invalid organization"))

	if year_of_settlement and not isinstance(year_of_settlement, int):
		frappe.throw(_("Invalid year of settlement"))

	return get_columns(), get_data(organization, year_of_settlement)


def get_columns():
	return [
		{
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"label": "Posting Date",
			"width": 200,
		},
		{
			"fieldname": "voucher_type",
			"label": "Voucher Type",
			# Using a Select field here to display the translated value while
			# also avoiding permission issues that would come with a Link field.
			# (A link would require read perms on DocType "DocType".)
			"fieldtype": "Select",
			"width": 200,
		},
		{
			"fieldname": "voucher_no",
			"label": "Voucher No",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 200,
		},
		{
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"label": "Grand Total",
			"width": 200,
		},
	]


def get_data(organization: Optional[str], year_of_settlement: Optional[int] = None):
	filters = {
		"docstatus": 1,
	}

	if organization:
		filters["organization"] = organization

	if year_of_settlement:
		filters["year_of_settlement"] = year_of_settlement

	data = []
	for posting_date, grand_total, voucher_name in frappe.get_list(
		"Sales Invoice",
		fields=[
			"posting_date",
			"base_grand_total",
			"name",
		],
		filters=filters,
		as_list=True,
	):
		data.append(
			(
				posting_date,
				"Sales Invoice",
				voucher_name,
				grand_total,
			)
		)

	for posting_date, paid, received, voucher_name, payment_type in frappe.get_list(
		"Payment Entry",
		fields=[
			"posting_date",
			"base_paid_amount",
			"base_received_amount",
			"name",
			"payment_type",
		],
		filters=filters,
		as_list=True,
	):
		data.append(
			(
				posting_date,
				"Payment Entry",
				voucher_name,
				received * -1 if payment_type == "Receive" else paid,
			)
		)

	return sorted(data, key=lambda row: row[0])
