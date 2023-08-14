# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe import _


class LandaDeliveriesAndPaymentsSummaries:
	def __init__(self, filters):
		self.filters = filters

	def run(self):
		return self.get_columns(), self.get_data()

	def get_base_filters(self, organization, year_of_settlement):
		filters = self.filters.copy()
		filters["docstatus"] = 1
		filters["organization"] = organization
		filters["year_of_settlement"] = year_of_settlement

		return filters

	def fetch_and_sum(self, doctype, pluck_field, extra_filters):
		return sum(frappe.get_list(doctype, pluck=pluck_field, filters=extra_filters))

	def get_data(self):
		data = []

		years_of_settlement = (
			[self.filters["year_of_settlement"]]
			if self.filters.get("year_of_settlement")
			else list(range(2021, datetime.now().year + 1))
		)

		organizations = (
			[self.filters["organization"]]
			if self.filters.get("organization")
			else frappe.get_list(
				"Organization", pluck="name", filters=[["parent_organization", "in", ["AVS", "AVL", "AVE"]]]
			)
		)

		for year_of_settlement in years_of_settlement:
			for organization in organizations:
				base_filters = self.get_base_filters(organization, year_of_settlement)

				delivery_filters = base_filters.copy()
				delivery_filters["is_return"] = 0
				delivery_totals = self.fetch_and_sum("Delivery Note", "base_grand_total", delivery_filters)

				return_filters = base_filters.copy()
				return_filters["is_return"] = 1
				return_totals = self.fetch_and_sum("Delivery Note", "base_grand_total", return_filters)

				payments_received_filters = base_filters.copy()
				payments_received_filters["payment_type"] = "Receive"
				payments_received_filters["party_type"] = "Customer"
				payments_received_amounts = -self.fetch_and_sum(
					"Payment Entry", "base_paid_amount", payments_received_filters
				)

				payments_sent_filters = base_filters.copy()
				payments_sent_filters["payment_type"] = "Pay"
				payments_sent_filters["party_type"] = "Customer"
				payments_sent_amounts = self.fetch_and_sum(
					"Payment Entry", "base_paid_amount", payments_sent_filters
				)

				data.append(
					{
						"organization": organization,
						"year_of_settlement": year_of_settlement,
						"outstanding_amount": delivery_totals
						+ return_totals
						+ payments_received_amounts
						+ payments_sent_amounts,
					}
				)

		return sorted(data, key=lambda row: row["organization"])

	def get_columns(self):
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


def execute(filters=None):
	return LandaDeliveriesAndPaymentsSummaries(filters).run()
