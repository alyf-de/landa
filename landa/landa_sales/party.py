import frappe
from erpnext.accounts.party import get_party_details
from frappe.contacts.doctype.address.address import (
	get_address_display,
)
from frappe.contacts.doctype.contact.contact import get_contact_details

EMPTY_CONTACT = {
	"contact_person": None,
	"contact_display": None,
	"contact_email": None,
	"contact_mobile": None,
	"contact_phone": None,
}


@frappe.whitelist()
def get_landa_party_details(
	party=None,
	account=None,
	party_type="Customer",
	company=None,
	posting_date=None,
	bill_date=None,
	price_list=None,
	currency=None,
	doctype=None,
	ignore_permissions=False,
	fetch_payment_terms_template=True,
	party_address=None,
	company_address=None,
	shipping_address=None,
	pos_profile=None,
):
	party_details = get_party_details(
		party,
		account,
		party_type,
		company,
		posting_date,
		bill_date,
		price_list,
		currency,
		doctype,
		ignore_permissions,
		fetch_payment_terms_template,
		party_address,
		company_address,
		shipping_address,
		pos_profile,
	)

	if party_type == "Customer" and party:
		customer = frappe.get_doc("Customer", party)

		set_billing_address(party_details, customer)
		set_billing_contact(party_details, customer, doctype)
		set_shipping_address(party_details, customer)
		set_shipping_contact(party_details, customer, doctype)

	return party_details


def set_billing_address(party_details, customer):
	party_details["customer_address"] = customer.default_billing_address
	party_details["address_display"] = get_address_display(
		customer.default_billing_address
	)


def set_billing_contact(party_details, customer, doctype):
	if customer.default_billing_contact:
		billing_contact = get_contact_details(customer.default_billing_contact)
	else:
		billing_contact = EMPTY_CONTACT

	if doctype == "Delivery Note":
		party_details.update(
			{
				"billing_contact": billing_contact.get("contact_person"),
				"billing_contact_display": billing_contact.get("contact_display"),
				"billing_contact_mobile": billing_contact.get("contact_mobile"),
				"billing_contact_phone": billing_contact.get("contact_phone"),
				"billing_contact_email": billing_contact.get("contact_email"),
			}
		)
	else:
		party_details.update(billing_contact)


def set_shipping_address(party_details, customer):
	party_details["shipping_address_name"] = customer.default_shipping_address
	party_details["shipping_address"] = get_address_display(
		customer.default_shipping_address
	)


def set_shipping_contact(party_details, customer, doctype):
	if customer.default_shipping_contact:
		shipping_contact = get_contact_details(customer.default_shipping_contact)
	else:
		shipping_contact = EMPTY_CONTACT

	if doctype == "Delivery Note":
		party_details.update(shipping_contact)
	else:
		party_details.update(
			{
				"shipping_contact": shipping_contact.get("contact_person"),
				"shipping_contact_display": shipping_contact.get("contact_display"),
				"shipping_contact_mobile": shipping_contact.get("contact_mobile"),
				"shipping_contact_phone": shipping_contact.get("contact_phone"),
				"shipping_contact_email": shipping_contact.get("contact_email"),
			}
		)
