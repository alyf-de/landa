import frappe
from frappe import _


def validate(doc, event):
	if doc.flags.ignore_mandatory or frappe.flags.in_test:
		return

	if doc.doctype == "Contact" and doc.user:
		add_data_from_linked_user(doc)

	if not doc.organization:
		frappe.throw(_("{0} should always be linked to an Organization").format(_(doc.doctype)))

	def append(link_doctype, link_name):
		doc.append(
			"links",
			{
				"link_doctype": link_doctype,
				"link_name": link_name,
				"link_title": link_name
			}
		)

	def check_write_permission(doctype, name):
		linked_doc = frappe.get_doc(doctype, name)
		linked_doc.check_permission("write")

	doc.links = []
	if doc.belongs_to_organization:
		# All records need to be linked to an Organization for permission
		# reasons, but not all should be displayed in the Organization record
		linked_doc = frappe.get_doc("Organization", doc.organization)
		linked_doc.check_permission("write")
		append("Organization", doc.organization)
	else:
		# If it doesn't belong to an Organization, then it also should not
		# belong to a Customer or Company
		doc.customer = None
		doc.company = None

	for (link_doctype, link_field) in (
		("Customer", "customer"),
		("Company", "company"),
		("LANDA Member", "landa_member"),
		("External Contact", "external_contact"),
	):
		doc_before_save = doc.get_doc_before_save()
		old_value = doc_before_save.get(link_field) if doc_before_save else None
		new_value = doc.get(link_field)
		if old_value != new_value:
			if old_value:
				check_write_permission(link_doctype, old_value)
			if new_value:
				check_write_permission(link_doctype, new_value)

		if new_value:
			append(link_doctype, new_value)


def add_data_from_linked_user(doc):
	doc.organization = doc.organization or frappe.db.get_value("User", doc.user, "organization")
	doc.landa_member = doc.landa_member or frappe.db.get_value("User", doc.user, "landa_member")
