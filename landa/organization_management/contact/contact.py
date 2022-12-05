from frappe.contacts.doctype.contact.contact import Contact


def after_insert(contact: Contact, event: str) -> None:
	"""
	Delete Contact if it's linked to User.

	Frappe automatically creates a Contact for each User. For data protection
	reasons we don't want this. Therefore we delete the contact again.
	"""
	if contact.user:
		contact.delete()


def validate(contact: Contact, event: str) -> None:
	set_primary_email_if_missing(contact)
	set_primary_phone_if_missing(contact)


def set_primary_email_if_missing(contact: Contact) -> bool:
	"""If no email_id is set as primary for a contact, set the first email_id as primary"""
	if not contact.email_ids or value_is_set(contact.email_ids, "is_primary"):
		return False

	contact.email_ids[0].is_primary = 1
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
				modified = True
				break

	if not value_is_set(contact.phone_nos, "is_primary_phone"):
		for phone in contact.phone_nos:
			if not is_mobile_number(phone.phone):
				phone.is_primary_phone = 1
				modified = True
				break

	return modified


def value_is_set(rows: list, fieldname: str) -> bool:
	return any(row.get(fieldname) for row in rows)


def is_mobile_number(number: str) -> bool:
	return "".join(filter(str.isdigit, number)).startswith(("01", "491", "00491"))
