# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note, make_sales_invoice
from frappe.utils.data import get_year_ending

from landa.landa_sales.utils import (
	validate_company_customer,
	validate_company_price_list,
	validate_year_of_settlement,
)
from landa.utils import update_doc


def before_validate(sales_order, event):
	for item in sales_order.items:
		item.delivery_date = get_year_ending(str(sales_order.year_of_settlement))

	if (not sales_order.tax_category) and frappe.db.exists("Tax Category", "Umsatzsteuer"):
		sales_order.tax_category = "Umsatzsteuer"


def validate(doc, event):
	validate_year_of_settlement(doc)
	validate_company_customer(doc.company, doc.customer)
	validate_company_price_list(doc.company, doc.selling_price_list)


def autoname(doc, event):
	"""Create Company-specific Sales Order name."""
	from landa.utils import get_new_name

	doc.name = get_new_name("BEST", doc.company, "Sales Order", doc.year_of_settlement)


def get_dashboard_data(data):
	data["transactions"] = [
		{
			"label": "Sales",
			"items": ["Delivery Note", "Sales Invoice"],
		},
	]
	return data


@frappe.whitelist()
def make_landa_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
	source_doc = frappe.get_doc("Sales Order", source_name)
	target_doc = make_sales_invoice(source_name, target_doc, ignore_permissions)

	update_doc(source_doc, target_doc)

	return target_doc


@frappe.whitelist()
def make_landa_delivery_note(source_name, target_doc=None, skip_item_mapping=False):
	source_doc = frappe.get_doc("Sales Order", source_name)
	target_doc = make_delivery_note(source_name, target_doc, skip_item_mapping)

	update_doc(source_doc, target_doc)

	return target_doc
