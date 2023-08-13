# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe
from frappe import _


class LandaDeliveriesAndPayments:
	def __init__(self, filters):
		self.filters = filters

	def run(self):
		if not ("organization" in self.filters):
			return [], []

		return self.get_columns(), self.get_data()

	def get_data(self):
		delivery_filters = self.filters.copy()
		delivery_filters["is_return"] = 0
		delivery_filters["docstatus"] = 1
		deliveries = frappe.get_list(
			"Delivery Note",
			fields=[
				"name",
				"posting_date",
				"base_grand_total as grand_total",
			],
			filters=delivery_filters,
		)
		assign_voucher_type_link(deliveries, "Delivery Note", _("Delivery Note"))

		return_filters = self.filters.copy()
		return_filters["is_return"] = 1
		return_filters["docstatus"] = 1
		returns = frappe.get_list(
			"Delivery Note",
			fields=[
				"name",
				"posting_date",
				"base_grand_total as grand_total",
			],
			filters=return_filters,
		)
		assign_voucher_type_link(returns, "Delivery Note", _("Sales Return"))

		payments_received_filters = self.filters.copy()
		payments_received_filters["payment_type"] = "Receive"
		payments_received_filters["party_type"] = "Customer"
		payments_received_filters["docstatus"] = 1
		payments_received = frappe.get_list(
			"Payment Entry",
			fields=[
				"name",
				"posting_date",
				"base_paid_amount as grand_total",
			],
			filters=payments_received_filters,
		)
		assign_voucher_type_link(payments_received, "Payment Entry", _("Incoming Payment"))

		for payment in payments_received:
			# received payments reduce the debt
			payment["grand_total"] = -1 * payment["grand_total"]

		payments_sent_filters = self.filters.copy()
		payments_sent_filters["payment_type"] = "Pay"
		payments_sent_filters["party_type"] = "Customer"
		payments_sent_filters["docstatus"] = 1
		payments_sent = frappe.get_list(
			"Payment Entry",
			fields=[
				"name",
				"posting_date",
				"base_paid_amount as grand_total",
			],
			filters=payments_sent_filters,
		)
		assign_voucher_type_link(payments_sent, "Payment Entry", _("Outgoing Payment"))

		data = deliveries + returns + payments_received + payments_sent

		data = sorted(data, key=lambda row: row["posting_date"])

		return data

	def get_columns(self):
		return [
			{
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"label": "Posting Date",
				"width": 200,
			},
			{
				"fieldname": "voucher_type",
				"fieldtype": "Data",
				"label": "Voucher Type",
				"width": 200,
			},
			{
				"fieldname": "grand_total",
				"fieldtype": "Currency",
				"label": "Grand Total",
				"width": 200,
			},
		]


def assign_voucher_type_link(items, doctype, label):
	for item in items:
		item[
			"voucher_type"
		] = f'<a href="/app/{doctype.replace(" ","-").lower()}/{item["name"]}" data-doctype="{doctype}" data-name="{item["name"]}">{label}</a>'


def execute(filters=None):
	return LandaDeliveriesAndPayments(filters).run()
