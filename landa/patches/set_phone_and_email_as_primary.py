import frappe


def execute():
	def value_not_set(rows, fieldname):
		return not any(row[fieldname] for row in rows)

	def number_is_mobile(number):
		return "".join(filter(str.isdigit, number)).startswith(("01","491","00491"))

	def set_doc_attr(doctype,name,field,value):
		doc=frappe.get_doc(doctype, name)
		setattr(doc, field, value)
		doc.save()

	def set_primary_email_if_missing(contact):
		"""If no email_id is set as primary for a contact, set the first email_id as primary"""
		contact_emails = frappe.get_list(
			"Contact Email",
			filters={"parent": contact},
			fields=["name", "is_primary"],
		)
		if contact_emails and value_not_set(contact_emails, "is_primary"):
			set_doc_attr("Contact Email",contact_emails[0]["name"],"is_primary", 1)

	def set_primary_phone_if_missing(contact):
		"""If no phone is set as primary mobile or primary phone for a contact,
		set the first mobile as primary mobile and the first not mobile as primary phone 
		(according to the first digits of the phone number)"""
		contact_phones = frappe.get_list(
			"Contact Phone",
			filters={"parent": contact},
			fields=["name", "phone", "is_primary_mobile_no", "is_primary_phone"],
		)
		if contact_phones and value_not_set(contact_phones, "is_primary_mobile_no") and value_not_set(
			contact_phones, "is_primary_phone"
		):
			mobile_is_set=False
			phone_is_set=False
			for contact_phone in contact_phones:
				if number_is_mobile(contact_phone["phone"]):
					if not mobile_is_set:
						set_doc_attr("Contact Phone",contact_phone["name"],"is_primary_mobile_no", 1)
						mobile_is_set=True
				else:
					if not phone_is_set:
						set_doc_attr("Contact Phone",contact_phone["name"],"is_primary_phone", 1)
						phone_is_set=True

	for contact in frappe.get_all(
		"Contact",
		or_filters={
			"phone": ("is", "not set"),
			"mobile_no": ("is", "not set"),
			"email_id": ("is", "not set"),
		},
		pluck="name",
	):
		set_primary_email_if_missing(contact)
		set_primary_phone_if_missing(contact)
