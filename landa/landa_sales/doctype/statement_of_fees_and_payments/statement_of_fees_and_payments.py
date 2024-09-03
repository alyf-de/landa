# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.docstatus import DocStatus
from frappe.model.document import Document
from frappe.utils.data import get_link_to_form
from pandas import DataFrame as df


class StatementofFeesandPayments(Document):
	def before_save(self):
		self.fetch_payments()
		self.fetch_sales()
		self.calculate_totals()

	def validate(self):
		if (
			existing := frappe.db.exists(
				"Statement of Fees and Payments",
				{
					"customer": self.customer,
					"company": self.company,
					"year_of_settlement": self.year_of_settlement,
					"docstatus": ("!=", DocStatus.cancelled()),
					"name": ("!=", self.name),
				},
			)
			and self.docstatus != DocStatus.cancelled()
		):
			frappe.throw(
				_(
					"A Statement of Fees and Payments for the same customer and year already exists: {0}"
				).format(get_link_to_form("Statement of Fees and Payments", existing))
			)

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
				"`tabSales Invoice Item`.base_amount as amount",
			],
		)

		if not invoice_rows:
			return

		rows_df = df.from_records(invoice_rows)

		rows_df["billed"] = rows_df["qty"].clip(lower=0)
		rows_df["credited"] = -1 * rows_df["qty"].clip(upper=0)
		rows_df["net_billed"] = rows_df["billed"] - rows_df["credited"]
		rows_df["rate"] = rows_df["amount"] / rows_df["net_billed"]

		rows_df.drop(columns="qty", inplace=True)
		rows_df = rows_df.groupby(["item_code", "item_name"]).sum().reset_index()

		self.sales = []
		self.extend("sales", rows_df.to_dict(orient="records"))

	def calculate_totals(self):
		self.sum_of_payments = sum(p.amount for p in self.payments)
		self.sum_of_sales = sum(s.amount for s in self.sales)
