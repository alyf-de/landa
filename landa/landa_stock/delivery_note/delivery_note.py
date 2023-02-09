import frappe
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
from frappe import _
from landa.utils import update_doc


def before_validate(delivery_note, event):
	"""Set Tax Category to 'Umsatzsteuer'"""

	if (not delivery_note.tax_category) and frappe.db.exists(
		"Tax Category", "Umsatzsteuer"
	):
		delivery_note.tax_category = "Umsatzsteuer"


def validate(delivery_note, event):
	"""Validate that only returnable items are returned."""
	if delivery_note.is_return:
		for item in delivery_note.items:
			if frappe.db.get_value("Item", item.item_code, "cannot_be_returned"):
				frappe.throw(_("Item {} cannot be returned").format(item.item_name))
				return


def on_submit(delivery_note, event):
	"""Auto-create Sales Invoice for Delivery Note."""
	# 2021-09-24: disabled for now, but kept in case preferences change in the future

	# from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
	#
	# if delivery_note.get('create_sales_invoice'):
	# 	sales_invoice = make_sales_invoice(delivery_note.get('name'))
	# 	sales_invoice.save()
	# 	sales_invoice.submit()
	pass


def autoname(doc, event):
	"""Create Company-specific Delivery Note name."""
	from landa.utils import get_new_name

	if doc.is_return:
		doc.name = get_new_name("RET", doc.company, "Delivery Note")
	else:
		doc.name = get_new_name("LIEF", doc.company, "Delivery Note")


@frappe.whitelist()
def make_landa_sales_invoice(source_name, target_doc=None, skip_item_mapping=False):
	source_doc = frappe.get_doc("Delivery Note", source_name)
	target_doc = make_sales_invoice(source_name, target_doc, skip_item_mapping)

	update_doc(source_doc, target_doc)

	return target_doc
