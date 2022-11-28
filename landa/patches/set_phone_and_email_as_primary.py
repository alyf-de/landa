import frappe


def execute():
	def value_not_set(rows, fieldname):
		return not any(row[fieldname] for row in rows)

	def number_is_mobile(number):
		def remove_non_digit_characters(number):
			return "".join(filter(str.isdigit, number))
		cleared_number = remove_non_digit_characters(number)
		return cleared_number.startswith(("01","491","00491"))

	def set_primary_email_if_missing(contact):
		"""If no email_id is set as primary for a contact, set the first email_id as primary"""
		contact_emails = frappe.get_list(
			"Contact Email",
			filters={"parent": contact},
			fields=["name", "is_primary"],
		)
		if contact_emails and value_not_set(contact_emails, "is_primary"):
			frappe.db.set_value(
				"Contact Email", contact_emails[0]["name"], "is_primary", 1
			)

	def set_primary_phone_if_missing(contact):
		"""If no phone is set as primary mobile or primary phone for a contact,
		set all phones as primary phone or primary phone according to the first digits of the phone number"""
		contact_phones = frappe.get_list(
			"Contact Phone",
			filters={"parent": contact},
			fields=["name", "phone", "is_primary_mobile_no", "is_primary_phone"],
		)
		if contact_phones and value_not_set(contact_phones, "is_primary_mobile_no") and value_not_set(
			contact_phones, "is_primary_phone"
		):
			for contact_phone in contact_phones:
				if number_is_mobile(contact_phone["phone"]):
					frappe.db.set_value(
						"Contact Phone",
						contact_phone["name"],
						"is_primary_mobile_no",
						1,
					)
				else:
					frappe.db.set_value(
						"Contact Phone", contact_phone["name"], "is_primary_phone", 1
					)

	contacts = frappe.get_list("Contact", pluck="name")
	for contact in contacts:
		set_primary_email_if_missing(contact)
		set_primary_phone_if_missing(contact)
