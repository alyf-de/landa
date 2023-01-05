# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import get_year_ending
import inspect
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote


def before_validate(sales_order, event):
	for item in sales_order.items:
		item.delivery_date = get_year_ending(str(sales_order.year_of_settlement))

	if (not sales_order.tax_category) and frappe.db.exists(
		"Tax Category", "Umsatzsteuer"
	):
		sales_order.tax_category = "Umsatzsteuer"


def autoname(doc, event):
	"""Create Company-specific Sales Order name."""
	from landa.utils import get_new_name

	doc.name = get_new_name("BEST", doc.company, "Sales Order")


def get_dashboard_data(data):
	data["transactions"] = [
		{
			"label": "Sales",
			"items": ["Delivery Note", "Sales Invoice"],
		},
	]
	return data
