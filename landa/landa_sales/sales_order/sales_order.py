# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note, make_sales_invoice
from frappe import _
from frappe.utils.data import get_year_ending

from landa.utils import update_doc


def before_validate(sales_order, event):
	for item in sales_order.items:
		item.delivery_date = get_year_ending(str(sales_order.year_of_settlement))

	if (not sales_order.tax_category) and frappe.db.exists("Tax Category", "Umsatzsteuer"):
		sales_order.tax_category = "Umsatzsteuer"


def validate(doc, event):
	if not doc.year_of_settlement:
		return

	for item in doc.items:
		from_year, to_year = frappe.db.get_value(
			"Item", item.item_code, ["valid_from_year", "valid_to_year"]
		)

		if (from_year and doc.year_of_settlement < from_year) or (
			to_year and doc.year_of_settlement > to_year
		):
			frappe.throw(
				_("Row {0}: Item {1} is not valid for year of settlement {2}.").format(
					item.idx, frappe.bold(item.item_name), frappe.bold(doc.year_of_settlement)
				)
			)


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
