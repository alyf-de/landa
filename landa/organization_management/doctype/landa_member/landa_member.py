# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt


import traceback

import frappe
from frappe import _
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.model.document import Document
from frappe.model.naming import make_autoname, revert_series_if_last

from landa.utils import (
	delete_dynamically_linked,
	delete_records_linked_to,
	get_member_and_organization,
)


class LANDAMember(Document):
	def autoname(self):
		"""Generate the unique member number (name field)

		Organization: AVL-001-0001, AVE-001-0001, ...
		Local group: AVL-001-01-0001, AVL-001-02-0001, ...
		"""
		if self.name:
			return
		self.name = make_autoname(f"{self.organization}-.####", "LANDA Member")

	def onload(self):
		load_address_and_contact(self)

	def validate(self):
		if frappe.db.get_value("Organization", self.organization, "is_group"):
			frappe.throw(
				_("Cannot be a member of organization {} because it is a group.").format(self.organization)
			)

		self.full_name = get_full_name(self.first_name, self.last_name)

	def on_trash(self):
		current_member = get_member_and_organization(frappe.session.user)[0]
		if current_member == self.name:
			frappe.throw(_("You cannot delete your own member record."))

		user = frappe.db.exists("User", {"landa_member": self.name})
		if user:
			frappe.delete_doc(
				"User",
				user,
				ignore_permissions=True,
				ignore_missing=True,
				delete_permanently=True,
			)

		delete_dynamically_linked("Address", self.doctype, self.name)
		delete_dynamically_linked("Contact", self.doctype, self.name)
		delete_records_linked_to("LANDA Member", self.name)

		self.revert_series()

	def revert_series(self):
		"""Decrease the naming counter when the newest member gets deleted."""
		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split("-")[-1])
		key = f"{self.name[:-number_part_len]}.{'#' * number_part_len}"
		revert_series_if_last(key, self.name)

	def on_update(self):
		organization = frappe.get_doc("Organization", self.organization)
		organization.address = self.address
		organization.save()


def get_full_name(first_name, last_name):
	return (first_name or "") + (" " if (last_name and first_name) else "") + (last_name or "")


def link_member_contacts_and_addresses_to_organization(member, organization):
	for address in frappe.get_all(
		"Address", filters={"link_doctype": "LANDA Member", "link_name": member.name}
	):
		if not frappe.db.exists(
			"Dynamic Link",
			{
				"link_doctype": "Organization",
				"link_name": organization.name,
				"parenttype": "Address",
				"parent": address.name,
			},
		):
			link = frappe.get_doc(
				{
					"doctype": "Dynamic Link",
					"link_doctype": "Organization",
					"link_name": organization.name,
					"parenttype": "Address",
					"parent": address.name,
				}
			)
			link.insert()

	for contact in frappe.get_all(
		"Contact", filters={"link_doctype": "LANDA Member", "link_name": member.name}
	):
		if not frappe.db.exists(
			"Dynamic Link",
			{
				"link_doctype": "Organization",
				"link_name": organization.name,
				"parenttype": "Contact",
				"parent": contact.name,
			},
		):
			link = frappe.get_doc(
				{
					"doctype": "Dynamic Link",
					"link_doctype": "Organization",
					"link_name": organization.name,
					"parenttype": "Contact",
					"parent": contact.name,
				}
			)
			link.insert()


@frappe.whitelist()
def link_contact_person(member_name):
	try:
		member = frappe.get_doc("LANDA Member", member_name)
		organization = frappe.get_doc("Organization", member.organization)
		link_member_contacts_and_addresses_to_organization(member, organization)
		frappe.msgprint(_("Contact person successfully added."))
	except Exception as e:
		print("An error occurred:")
		frappe.throw(traceback.format_exc())


def unlink_member_contacts_and_addresses_from_organization(member, organization):
	for address in frappe.get_all(
		"Address", filters={"link_doctype": "LANDA Member", "link_name": member.name}
	):
		link = frappe.db.exists(
			"Dynamic Link",
			{
				"link_doctype": "Organization",
				"link_name": organization.name,
				"parenttype": "Address",
				"parent": address.name,
			},
		)
		if link:
			frappe.delete_doc("Dynamic Link", link)

	for contact in frappe.get_all(
		"Contact", filters={"link_doctype": "LANDA Member", "link_name": member.name}
	):
		link = frappe.db.exists(
			"Dynamic Link",
			{
				"link_doctype": "Organization",
				"link_name": organization.name,
				"parenttype": "Contact",
				"parent": contact.name,
			},
		)
		if link:
			frappe.delete_doc("Dynamic Link", link)


@frappe.whitelist()
def unlink_contact_person(member_name):
	member = frappe.get_doc("LANDA Member", member_name)
	organization = frappe.get_doc("Organization", member.organization)

	unlink_member_contacts_and_addresses_from_organization(member, organization)

	frappe.msgprint(_("Contact person successfully removed."))
