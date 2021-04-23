from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice

def on_submit(delivery_note, event):
	"""Auto-create Sales Invoice for Delivery Note."""
	if delivery_note.get('create_sales_invoice'):
		sales_invoice = make_sales_invoice(delivery_note.get('name'))
		sales_invoice.save()
		sales_invoice.submit()
