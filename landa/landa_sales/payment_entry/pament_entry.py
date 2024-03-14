import frappe
from frappe import _

# We need to set and validate the organization in the backend because the field
# is read-only and does not always get filled automatically (e.g. when creating
# a Payment Entry from a Sales Invoice).


def before_validate(payment_entry, event):
	set_organization(payment_entry)


def validate(payment_entry, event):
	if not payment_entry.organization:
		frappe.throw(_("Payment Entry must be linked to an organization."))


def set_organization(payment_entry):
	if payment_entry.party_type == "Customer" and payment_entry.party:
		payment_entry.organization = frappe.get_value("Customer", payment_entry.party, "organization")


def autoname(doc, event):
	"""Create Company-specific Payment Entry name."""
	from landa.utils import get_new_name

	doc.name = get_new_name("ZAHL", doc.company, "Payment Entry")
