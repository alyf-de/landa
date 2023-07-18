# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt


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


def get_full_name(first_name, last_name):
	return (first_name or "") + (" " if (last_name and first_name) else "") + (last_name or "")


@frappe.whitelist()
def link_contact_person(member_name):
	member = frappe.get_doc("LANDA Member", member_name)
	organization = frappe.get_doc("Organization", member.organization)
	link_member_to_organization(member, organization)
	frappe.msgprint(_("Contact person successfully added."))


def link_member_to_organization(member, organization):
	member_address = frappe.get_doc(
		"Address", member.first_name + " " + member.last_name + " - " + member.name
	)
	member_contact = frappe.get_doc("Contact", member.first_name + "-" + member.name)
	organization_address = frappe.get_doc(
		"Address", organization.organization_name + " - " + organization.name
	)
	organization_address.address_type = member_address.address_type
	organization_address.address_line1 = member_address.address_line1
	organization_address.address_line2 = member_address.address_line2
	organization_address.city = member_address.city
	organization_address.state = member_address.state
	organization_address.pincode = member_address.pincode
	organization_address.save()
	organization.save()


@frappe.whitelist()
def unlink_contact_person(member_name):
	member = frappe.get_doc("LANDA Member", member_name)
	organization = frappe.get_doc("Organization", member.organization)

	unlink_member_from_organization(organization)

	frappe.msgprint(_("Contact person successfully removed."))


def unlink_member_from_organization(organization):
	organization_address = frappe.get_doc(
		"Address", organization.organization_name + " - " + organization.name
	)
	organization_address.delete()
