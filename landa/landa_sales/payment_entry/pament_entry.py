import frappe


def before_validate(payment_entry, event):
	set_organization(payment_entry)


def set_organization(payment_entry):
	if payment_entry.party_type == "Customer" and payment_entry.party:
		payment_entry.organization = frappe.get_value(
			"Customer", payment_entry.party, "organization"
		)


def autoname(doc, event):
	"""Create Company-specific Payment Entry name."""
	from landa.utils import get_new_name

	doc.name = get_new_name("ZAHL", doc.company, "Payment Entry")
