# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import get_year_ending
import inspect
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note


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

@frappe.whitelist()
def make_landa_delivery_note(source_name, target_doc=None, skip_item_mapping=False):
	target_doc = make_delivery_note(source_name, target_doc, skip_item_mapping)

	sales_order = frappe.get_doc("Sales Order", source_name)

	target_doc.update({
		"shipping_address_name": sales_order.shipping_address_name,
		"shipping_address": sales_order.shipping_address,
		"contact_person": sales_order.shipping_contact,
		"contact_display": sales_order.shipping_contact_display,
		"contact_email": sales_order.shipping_contact_email,
		"contact_mobile": sales_order.shipping_contact_mobile,
		"contact_phone": sales_order.shipping_contact_phone,
		"customer_address": sales_order.customer_address,
		"address_display": sales_order.address_display,
		"billing_contact": sales_order.contact_person,
		"billing_contact_display": sales_order.contact_display,
		"billing_contact_email": sales_order.contact_email,
		"billing_contact_mobile": sales_order.contact_mobile,
		"billing_contact_phone": sales_order.contact_phone,
	})

	return target_doc