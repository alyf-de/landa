import frappe
from frappe import _
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice


def validate(delivery_note, event):
	"""Validate that only returnable items are returned."""
	if delivery_note.is_return:
		for item in delivery_note.items:
			if frappe.db.get_value('Item', item.item_code, 'cannot_be_returned'):
				frappe.throw(_('Item {} cannot be returned').format(item.item_name))
				return


def on_submit(delivery_note, event):
	"""Auto-create Sales Invoice for Delivery Note."""
	if delivery_note.get('create_sales_invoice'):
		sales_invoice = make_sales_invoice(delivery_note.get('name'))
		sales_invoice.save()
		sales_invoice.submit()

@frappe.whitelist()
def get_items(year):
	fields = ['item_code', 'item_name', 'cannot_be_returned', 'description']
	items = frappe.get_list('Item',
		filters={
			'valid_to_year': ["<=", year],
			'valid_from_year': [">=", year],
			'has_variants': False
		},
		fields=fields,
	)

	items.extend(frappe.get_list('Item',
		filters={
			'valid_to_year': 0,
			'valid_from_year': 0,
			'has_variants': False
		},
		fields=fields,
	))

	for item in items:
		item.qty = 0
		item.uom = 'Nos'
		item.uom_factor = 1
		item.rate = 1 # TODO: Set correct rate.

	return items
