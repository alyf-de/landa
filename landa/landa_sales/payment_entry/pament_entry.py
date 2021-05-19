import frappe


def before_validate(payment_entry, event):
	set_organization(payment_entry)


def set_organization(payment_entry):
	if payment_entry.party_type == 'Customer' and payment_entry.party:
		payment_entry.organization = frappe.get_value('Customer', payment_entry.party, 'organization')
