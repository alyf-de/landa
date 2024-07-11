# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.docstatus import DocStatus
from frappe.model.document import Document
from pandas import DataFrame as df


class StatementofFeesandPayments(Document):
	def before_save(self):
		self.fetch_payments()
		self.fetch_sales()
		self.calculate_totals()

	def fetch_payments(self):
		self.payments = []
		for pe in frappe.get_list(
			"Payment Entry",
			filters={
				"company": self.company,
				"party_type": "Customer",
				"party": self.customer,
				"docstatus": DocStatus.submitted(),
				"year_of_settlement": self.year_of_settlement,
			},
			fields=[
				"name",
				"reference_date",
				"payment_type",
				"base_paid_amount",
			],
		):
			self.append(
				"payments",
				{
					"payment_entry": pe.name,
					"payment_type": pe.payment_type,
					"reference_date": pe.reference_date,
					"amount": pe.base_paid_amount if pe.payment_type == "Receive" else -pe.base_paid_amount,
				},
			)

	def fetch_sales(self):
		invoice_rows = frappe.get_list(
			"Sales Invoice",
			filters={
				"company": self.company,
				"customer": self.customer,
				"docstatus": DocStatus.submitted(),
				"year_of_settlement": self.year_of_settlement,
			},
			fields=[
				"`tabSales Invoice Item`.item_code as item_code",
				"`tabSales Invoice Item`.item_name as item_name",
				"`tabSales Invoice Item`.qty as qty",
				"`tabSales Invoice Item`.base_net_amount as amount",
			],
		)

		if not invoice_rows:
			return

		invoice_rows = df.from_records(invoice_rows)
		invoice_rows["delivered"] = invoice_rows["qty"].clip(lower=0)
		invoice_rows["returned"] = -1 * invoice_rows["qty"].clip(upper=0)
		invoice_rows["net_delivered"] = invoice_rows["delivered"] - invoice_rows["returned"]
		invoice_rows["rate"] = invoice_rows["amount"] / invoice_rows["net_delivered"]
		invoice_rows.drop(columns="qty", inplace=True)

		self.sales = []
		self.extend("sales", invoice_rows.to_dict(orient="records"))

	def calculate_totals(self):
		self.sum_of_payments = sum(p.amount for p in self.payments)
		self.sum_of_sales = sum(s.amount for s in self.sales)
