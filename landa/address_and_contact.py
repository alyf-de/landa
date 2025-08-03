import frappe
from frappe import _


def before_validate(doc, event):
	if frappe.flags.in_test:
		doc.flags.ignore_mandatory = True


def validate(doc, event):
	"""
	Set explicit links to Customer, LANDA Member and Organization in the parent
	doc, if they are found in the child table. This lets us apply user
	permissions on child table links to the parent doc.
	"""

	validate_member_link(doc)
	validate_link_permissions(doc)

	linked_doctypes = {link.link_doctype for link in doc.links}
	mandatory_links = {
		"Company",
		"LANDA Member",
		"Organization",
		"Customer",
		"Supplier",
		"External Contact",
	}
	if (
		not linked_doctypes.intersection(mandatory_links)
		and not doc.flags.ignore_mandatory
		and not frappe.flags.in_test  # needed for frappe test_records to pass
	):
		frappe.throw(
			# fmt: off
			_("This document should be linked to at least one Company, LANDA Member, Organization, Customer or Supplier")
			# fmt: on
		)

	doc.organization = None
	for link in doc.links:
		if link.link_doctype == "Customer":
			doc.organization = frappe.db.get_value("Customer", link.link_name, "organization")

		if link.link_doctype == "LANDA Member":
			doc.organization = frappe.db.get_value("LANDA Member", link.link_name, "organization")

		if link.link_doctype == "Organization":
			doc.organization = link.link_name

		if link.link_doctype == "External Contact":
			doc.organization = frappe.db.get_value("External Contact", link.link_name, "organization")

		if link.link_doctype == "Supplier":
			doc.organization = frappe.db.get_value("Supplier", link.link_name, "organization")


def validate_link_permissions(doc):
	"""Linking an Address or Contact should be treated like writing to the linked doc."""
	if doc.flags.ignore_permissions:
		return

	new_links = {(link.link_doctype, link.link_name) for link in doc.links}
	check_link_permissions(new_links)

	doc_before_save = doc.get_doc_before_save()
	if not doc_before_save:
		return

	# Write permission is also necessary on removed links
	old_links = {(link.link_doctype, link.link_name) for link in doc_before_save.links}
	check_link_permissions(old_links - new_links)


def check_link_permissions(links):
	for dt, name in links:
		linked_doc = frappe.get_doc(dt, name)
		try:
			linked_doc.check_permission("write")
		except frappe.PermissionError:
			if linked_doc.doctype == "Customer":
				frappe.clear_messages()
				# Overly specific error message that was requested because it is
				# easier to understand than a general permission error.
				frappe.throw(
					_("This Address / Contact is linked to a Customer.")
					+ "\n"
					+ _(
						"Please contact someone who can edit the Customer, e.g. an employee of your regional organization."
					)
				)


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
