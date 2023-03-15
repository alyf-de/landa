import frappe
# from frappe import _


def validate(doc, event):
	if doc.flags.ignore_mandatory or frappe.flags.in_test:
		return

	if doc.doctype == "Contact" and doc.user:
		add_data_from_linked_user(doc)

	def append(link_doctype, link_name):
		doc.append("links", {"link_doctype": link_doctype, "link_name": link_name})

	doc.links = []
	if doc.belongs_to_organization:
		# All records need to be linked to an Organization for permission
		# reasons, but not all should be displayed in the Organization record
		linked_doc = frappe.get_doc("Organization", doc.organization)
		linked_doc.check_permission("write")
		append("Organization", doc.organization)
	else:
		# If it doesn't belong to an Organization, then it also should not
		# belong to a Customer
		doc.customer = None

	for (link_doctype, link_name) in (
		("Customer", doc.customer),
		("LANDA Member", doc.landa_member),
		("External Contact", doc.external_contact),
	):
		if not link_name:
			continue
		linked_doc = frappe.get_doc(link_doctype, link_name)
		linked_doc.check_permission("write")
		append(link_doctype, link_name)


def add_data_from_linked_user(doc):
	doc.organization = doc.organization or frappe.db.get_value("User", doc.user, "organization")
	doc.landa_member = doc.landa_member or frappe.db.get_value("User", doc.user, "landa_member")
