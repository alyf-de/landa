from frappe.contacts.doctype.contact.contact import Contact


def validate(contact: Contact, event: str) -> None:
	set_primary_email_if_missing(contact)
	set_primary_phone_if_missing(contact)


def set_primary_email_if_missing(contact: Contact) -> bool:
	"""If no email_id is set as primary for a contact, set the first email_id as primary"""
	if not contact.email_ids or value_is_set(contact.email_ids, "is_primary"):
		return False

	contact.email_ids[0].is_primary = 1
	contact.email_id = contact.email_ids[0].email_id
	return True


def set_primary_phone_if_missing(contact: Contact) -> bool:
	"""If no phone is set as primary mobile or primary phone for a contact,
	set the first mobile as primary mobile and the first not mobile as primary phone
	(according to the first digits of the phone number)"""
	modified = False
	if not contact.phone_nos:
		return modified

	if not value_is_set(contact.phone_nos, "is_primary_mobile_no"):
		for phone in contact.phone_nos:
			if is_mobile_number(phone.phone):
				phone.is_primary_mobile_no = 1
				contact.mobile_no = phone.phone
				modified = True
				break

	if not value_is_set(contact.phone_nos, "is_primary_phone"):
		for phone in contact.phone_nos:
			if not is_mobile_number(phone.phone):
				phone.is_primary_phone = 1
				contact.phone = phone.phone
				modified = True
				break

	return modified


def value_is_set(rows: list, fieldname: str) -> bool:
	return any(row.get(fieldname) for row in rows)


def is_mobile_number(number: str) -> bool:
	return "".join(filter(str.isdigit, number)).startswith(("01", "491", "00491"))
