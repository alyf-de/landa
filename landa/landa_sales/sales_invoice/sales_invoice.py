import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from landa.utils import update_doc


def before_validate(sales_invoice, event):
	"""Set Tax Category to 'Umsatzsteuer'"""
	import frappe

	if (not sales_invoice.tax_category) and frappe.db.exists(
		"Tax Category", "Umsatzsteuer"
	):
		sales_invoice.tax_category = "Umsatzsteuer"


def autoname(doc, event):
	"""Create Company-specific Sales Invoice name."""
	from landa.utils import get_new_name

	if doc.is_return:
		doc.name = get_new_name("GUTS", doc.company, "Sales Invoice")
	else:
		doc.name = get_new_name("RECH", doc.company, "Sales Invoice")


@frappe.whitelist()
def make_landa_delivery_note(source_name, target_doc=None):
	source_doc = frappe.get_doc("Sales Invoice", source_name)
	target_doc = make_delivery_note(source_name, target_doc)

	update_doc(source_doc, target_doc)

	return target_doc
