# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from frappe.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)

# import frappe
# from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname, revert_series_if_last

from landa.organization_management.doctype.landa_member.landa_member import get_full_name


class ExternalContact(Document):
	def autoname(self):
		"""Generate the unique external contact number (name field)

		Organization:				AVL-001-0001, AVE-001-0001, ...
		Local group:				AVL-001-01-0001, AVL-001-02-0001, ...
		"""
		if self.name:
			return

		self.name = make_autoname("EXT-" + self.organization + "-.####", "External Contact")

	def validate(self):
		self.full_name = get_full_name(self.first_name, self.last_name)

	def onload(self):
		load_address_and_contact(self)

	def on_trash(self):
		delete_contact_and_address(self.doctype, self.name)
		self.revert_series()

	def revert_series(self):
		"""Decrease the naming counter when the newest external contact gets deleted."""
		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split("-")[-1])
		key = self.name[:-number_part_len] + "." + "#" * number_part_len

		revert_series_if_last(key, self.name)
