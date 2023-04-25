import frappe
from frappe import _


def validate(doc, event):
	"""
	Set explicit links to Customer, LANDA Member and Organization in the parent
	doc, if they are found in the child table. This lets us apply user
	permissions on child table links to the parent doc.
	"""

	validate_member_link(doc)

	linked_doctypes = {link.link_doctype for link in doc.links}
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
		and not frappe.flags.in_test  # needed for frappe test_records to pass
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
			doc.organization = frappe.db.get_value("External Contact", link.link_name, "organization")


def validate_member_link(doc):
	if doc.doctype == "Contact" and doc.user:
		member = frappe.get_value("User", doc.user, "landa_member")

		if member and not member_link_exists(doc, member):
			doc.append("links", {"link_doctype": "LANDA Member", "link_name": member})

		if (
			not member_link_exists(doc, member)
			and not doc.flags.ignore_mandatory
			and not frappe.flags.in_test
		):
			frappe.throw(_("Contacts of users must be linked to a LANDA Member"))


def member_link_exists(doc, member):
	return any(x for x in doc.links if x.link_doctype == "LANDA Member" and x.link_name == member)


def on_trash(doc, event):
	from landa.utils import delete_records_linked_to

	delete_records_linked_to(doc.doctype, doc.name)
