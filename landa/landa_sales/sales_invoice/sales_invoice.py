from typing import TYPE_CHECKING

import frappe

if TYPE_CHECKING:
	from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from frappe import _

from landa.utils import update_doc


def before_validate(doc: "SalesInvoice", event: str):
	"""Set Tax Category to 'Umsatzsteuer'"""
	import frappe

	if (not doc.tax_category) and frappe.db.exists("Tax Category", "Umsatzsteuer"):
		doc.tax_category = "Umsatzsteuer"


def autoname(doc: "SalesInvoice", event: str):
	"""Create Company-specific Sales Invoice name."""
	from landa.utils import get_new_name

	if doc.is_return:
		doc.name = get_new_name("GUTS", doc.company, "Sales Invoice", doc.year_of_settlement)
	else:
		doc.name = get_new_name("RECH", doc.company, "Sales Invoice", doc.year_of_settlement)


@frappe.whitelist()
def make_landa_delivery_note(source_name, target_doc=None):
	source_doc = frappe.get_doc("Sales Invoice", source_name)
	target_doc = make_delivery_note(source_name, target_doc)

	update_doc(source_doc, target_doc)

	return target_doc


def on_submit(doc: "SalesInvoice", event: str):
	if not doc.contact_person:
		frappe.throw(_("Please set a Billing Contact before submitting the Sales Invoice."))

	if not doc.customer_address:
		frappe.throw(_("Please set a Billing Address before submitting the Sales Invoice."))
