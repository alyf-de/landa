import frappe
from frappe.contacts.doctype.contact.contact import Contact
from frappe.utils import update_progress_bar


def execute():
	frappe.db.auto_commit_on_many_writes = True

	contacts = frappe.get_all(
		"Contact",
		or_filters={
			"phone": ("is", "not set"),
			"mobile_no": ("is", "not set"),
			"email_id": ("is", "not set"),
		},
		pluck="name",
	)
	total = len(contacts)
	for i, contact_name in enumerate(contacts):
		update_progress_bar("Setting primary email and phone", i, total)
		contact = frappe.get_doc("Contact", contact_name)
		set_primary_email_if_missing(contact)
		set_primary_phone_if_missing(contact)
		contact.save(ignore_permissions=True, ignore_version=True)

	frappe.db.auto_commit_on_many_writes = False


def value_is_set(rows: list, fieldname: str) -> bool:
	return any(row.get(fieldname) for row in rows)


def number_is_mobile(number: str) -> bool:
	return "".join(filter(str.isdigit, number)).startswith(("01", "491", "00491"))


def set_primary_email_if_missing(contact: Contact) -> None:
	"""If no email_id is set as primary for a contact, set the first email_id as primary"""
	if not contact.email_ids or value_is_set(contact.email_ids, "is_primary"):
		return

	contact.email_ids[0].is_primary = 1


def set_primary_phone_if_missing(contact: Contact) -> None:
	"""If no phone is set as primary mobile or primary phone for a contact,
	set the first mobile as primary mobile and the first not mobile as primary phone
	(according to the first digits of the phone number)"""
	if not contact.phone_nos:
		return

	if not value_is_set(contact.phone_nos, "is_primary_mobile_no"):
		for phone in contact.phone_nos:
			if number_is_mobile(phone.phone):
				phone.is_primary_mobile_no = 1
				break

	if not value_is_set(contact.phone_nos, "is_primary_phone"):
		for phone in contact.phone_nos:
			if not number_is_mobile(phone.phone):
				phone.is_primary_phone = 1
				break
