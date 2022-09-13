import frappe
from frappe import _


def validate(doc, event):
	"""
	Set explicit links to Customer, LANDA Member and Organization in the parent
	doc, if they are found in the child table. This lets us apply user
	permissions on child table links to the parent doc.
	"""
	if doc.doctype == "Contact" and doc.user and not doc.links:
		member = frappe.get_value("User", doc.user, "landa_member")
		if member:
			doc.append("links", {"link_doctype": "LANDA Member", "link_name": member})

	linked_doctypes = set(link.link_doctype for link in doc.links)
	mandatory_links = {
		"Company",
		"LANDA Member",
		"Organization",
		"Customer",
		"External Contact",
	}
	if (
		not linked_doctypes.intersection(mandatory_links)
		and not doc.flags.ignore_mandatory
	):
		frappe.throw(
			# fmt: off
			_("This document should be linked to at least one Company, LANDA Member, Organization or Customer")
			# fmt: on
		)

	doc.customer = ""
	doc.landa_member = ""
	doc.organization = ""

	for link in doc.links:
		if link.link_doctype == "Customer":
			doc.customer = link.link_name
			doc.organization = link.link_name

		if link.link_doctype == "LANDA Member":
			doc.landa_member = link.link_name
			doc.organization = frappe.db.get_value("LANDA Member", link.link_name, "organization")

		if link.link_doctype == "Organization":
			doc.organization = link.link_name

		if link.link_doctype == "External Contact":
			doc.organization = frappe.db.get_value(
				"External Contact", link.link_name, "organization"
			)
