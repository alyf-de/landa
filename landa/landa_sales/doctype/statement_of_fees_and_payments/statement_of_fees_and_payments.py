# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.docstatus import DocStatus
from frappe.model.document import Document
from frappe.utils.data import get_link_to_form
from pandas import DataFrame as df

from landa.utils import get_new_name


class StatementofFeesandPayments(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.landa_sales.doctype.landa_item_sales_summary.landa_item_sales_summary import (
			LANDAItemSalesSummary,
		)
		from landa.landa_sales.doctype.landa_payment_row.landa_payment_row import LANDAPaymentRow

		amended_from: DF.Link | None
		billing_address: DF.Link | None
		billing_address_display: DF.SmallText | None
		billing_contact: DF.Link | None
		company: DF.Link
		company_address: DF.Link | None
		company_address_display: DF.SmallText | None
		customer: DF.Link
		customer_name: DF.Data | None
		organization: DF.Link | None
		payments: DF.Table[LANDAPaymentRow]
		posting_date: DF.Date
		sales: DF.Table[LANDAItemSalesSummary]
		sum_of_payments: DF.Currency
		sum_of_sales: DF.Currency
		year_of_settlement: DF.Int

	# end: auto-generated types
	def autoname(self):
		self.name = get_new_name("BA", self.company, self.doctype, self.year_of_settlement)

	def before_save(self):
		self.fetch_payments()
		self.fetch_sales()
		self.calculate_totals()

	def validate(self):
		if self.docstatus == DocStatus.cancelled():
			return

		if not self.organization:
			frappe.throw(_("This Statement of Fees and Payments must be linked to an Organization"))

		if existing := frappe.db.exists(
			"Statement of Fees and Payments",
			{
				"customer": self.customer,
				"company": self.company,
				"year_of_settlement": self.year_of_settlement,
				"posting_date": self.posting_date,
				"docstatus": ("!=", DocStatus.cancelled()),
				"name": ("!=", self.name),
			},
		):
			frappe.throw(
				_("This Statement of Fees and Payments already exists: {0}").format(
					get_link_to_form("Statement of Fees and Payments", existing)
				)
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
			order_by="reference_date ASC",
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

		rows_df = rows_df.drop(columns="qty")
		rows_df = rows_df.groupby(["item_code", "item_name"]).sum().reset_index()

		# NOTE: rate must be calculated after summing up the rows
		rows_df["rate"] = rows_df["amount"] / rows_df["net_billed"]
		# when net_billed is 0, rate is NaN
		rows_df["rate"] = rows_df["rate"].fillna(0)

		self.sales = []
		self.extend("sales", rows_df.to_dict(orient="records"))

	def calculate_totals(self):
		self.sum_of_payments = sum(p.amount for p in self.payments)
		self.sum_of_sales = sum(s.amount for s in self.sales)
