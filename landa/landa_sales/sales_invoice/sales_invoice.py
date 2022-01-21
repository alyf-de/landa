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
