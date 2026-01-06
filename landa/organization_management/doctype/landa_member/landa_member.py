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
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_information: DF.Data | None
		date_of_birth: DF.Date | None
		first_name: DF.Data | None
		fishing_permit_number: DF.Data | None
		full_name: DF.Data | None
		has_fishing_permit: DF.Check
		has_key: DF.Check
		has_special_yearly_fishing_permit_1: DF.Check
		has_special_yearly_fishing_permit_2: DF.Check
		has_special_yearly_fishing_permit_3: DF.Check
		has_special_yearly_fishing_permit_4: DF.Check
		has_special_yearly_fishing_permit_5: DF.Check
		has_special_yearly_fishing_permit_6: DF.Check
		has_special_yearly_fishing_permit_7: DF.Check
		is_supporting_member: DF.Check
		issuing_authority: DF.Data | None
		last_name: DF.Data | None
		magazine_recipient: DF.Check
		member_since: DF.Date | None
		nationality: DF.Data | None
		organization: DF.Link
		organization_name: DF.Data | None
		permit_expiration_date: DF.Date | None
		permit_is_valid_for_life: DF.Check
		permit_issue_date: DF.Date | None
		youth_membership: DF.Check

	# end: auto-generated types
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
def clear_special_yearly_fishing_permits(members):
	"""Remove all checkboxes in "Erlaubnisscheine Gewässerfonds" for the given members."""
	members = frappe.parse_json(members)

	permit_fields = [
		"has_special_yearly_fishing_permit_1",
		"has_special_yearly_fishing_permit_2",
		"has_special_yearly_fishing_permit_3",
		"has_special_yearly_fishing_permit_4",
		"has_special_yearly_fishing_permit_5",
		"has_special_yearly_fishing_permit_6",
		"has_special_yearly_fishing_permit_7",
	]

	for member in members:
		doc = frappe.get_doc("LANDA Member", str(member))
		for field in permit_fields:
			doc.set(field, 0)
			doc.save()


def get_address_or_contact(doctype: str, landa_member: str):
	"""Returns a single Address or Contact linked to the given LANDA member.

	If there are no or multiple linked addresses or contacts, None is returned.
	"""
	filters = [
		["Dynamic Link", "link_doctype", "=", "LANDA Member"],
		["Dynamic Link", "link_name", "=", landa_member],
	]
	if doctype == "Address":
		filters.append(["disabled", "=", 0])

	records = frappe.get_list(
		doctype,
		filters=filters,
		pluck="name",
		limit=2,
	)
	return frappe.get_doc(doctype, records[0]) if len(records) == 1 else None
