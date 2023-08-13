# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe


class LandaDeliveriesAndPaymentsSummaries:
	def __init__(self, filters):
		self.filters = filters

	def run(self):
		return self.get_columns(), self.get_data()

	def get_data(self):
		data = []

		if self.filters.get("year_of_settlement"):
			years_of_settlement = [self.filters["year_of_settlement"]]
		else:
			from datetime import datetime

			years_of_settlement = [year for year in range(2021, datetime.now().year + 1)]

		if self.filters.get("organization"):
			organizations = [self.filters.get("organization")]
		else:
			organizations = frappe.get_list(
				"Organization", pluck="name", filters=[["parent_organization", "in", ["AVS", "AVL", "AVE"]]]
			)

		for year_of_settlement in years_of_settlement:
			for organization in organizations:
				delivery_filters = self.filters.copy()
				delivery_filters["is_return"] = 0
				delivery_filters["docstatus"] = 1
				delivery_filters["organization"] = organization
				delivery_filters["year_of_settlement"] = year_of_settlement
				delivery_totals = frappe.get_list(
					"Delivery Note",
					pluck="base_grand_total",
					filters=delivery_filters,
				)

				return_filters = self.filters.copy()
				return_filters["is_return"] = 1
				return_filters["docstatus"] = 1
				return_filters["organization"] = organization
				return_filters["year_of_settlement"] = year_of_settlement
				return_totals = frappe.get_list(
					"Delivery Note",
					pluck="base_grand_total",
					filters=return_filters,
				)

				payments_received_filters = self.filters.copy()
				payments_received_filters["payment_type"] = "Receive"
				payments_received_filters["party_type"] = "Customer"
				payments_received_filters["docstatus"] = 1
				payments_received_filters["organization"] = organization
				payments_received_filters["year_of_settlement"] = year_of_settlement
				payments_received_amounts = frappe.get_list(
					"Payment Entry",
					pluck="base_paid_amount",
					filters=payments_received_filters,
				)

				# received payments reduce the debt
				payments_received_amounts = [-num for num in payments_received_amounts]

				payments_sent_filters = self.filters.copy()
				payments_sent_filters["payment_type"] = "Pay"
				payments_sent_filters["party_type"] = "Customer"
				payments_sent_filters["docstatus"] = 1
				payments_sent_filters["organization"] = organization
				payments_sent_filters["year_of_settlement"] = year_of_settlement
				payments_sent_amounts = frappe.get_list(
					"Payment Entry",
					pluck="base_paid_amount",
					filters=payments_sent_filters,
				)

				outstanding_amount = (
					sum(delivery_totals)
					+ sum(return_totals)
					+ sum(payments_received_amounts)
					+ sum(payments_sent_amounts)
				)

				data.append(
					{
						"organization": organization,
						"year_of_settlement": year_of_settlement,
						"outstanding_amount": outstanding_amount,
					}
				)

		data = sorted(data, key=lambda row: row["organization"])

		return data

	def get_columns(self):
		return [
			{
				"fieldname": "organization",
				"fieldtype": "Link",
				"options": "Organization",
				"label": "Organization",
				"width": 200,
			},
			{
				"fieldname": "year_of_settlement",
				"fieldtype": "Data",
				"label": "Year of Settlement",
				"disable_total": True,
				"width": 200,
			},
			{
				"fieldname": "outstanding_amount",
				"fieldtype": "Currency",
				"label": "Outstanding Amount",
				"width": 200,
			},
		]


def execute(filters=None):
	return LandaDeliveriesAndPaymentsSummaries(filters).run()
