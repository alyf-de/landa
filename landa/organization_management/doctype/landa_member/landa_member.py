# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.model.naming import make_autoname
from frappe.model.naming import revert_series_if_last

from landa.utils import delete_records_linked_to, delete_dynamically_linked, get_member_and_organization


class LANDAMember(Document):

	def autoname(self):
		"""Generate the unique member number (name field)

		Organization:				AVL-001-0001, AVE-001-0001, ...
		Local group:				AVL-001-01-0001, AVL-001-02-0001, ...
		"""
		if self.name:
			return

		self.name = make_autoname(self.organization + '-.####', 'LANDA Member')

	def onload(self):
		load_address_and_contact(self)

	def validate(self):
		organization_is_group = lambda: frappe.db.get_value('Organization', self.organization, 'is_group')

		if organization_is_group():
			frappe.throw(_('Cannot be a member of organization {} because it is a group.').format(self.organization))

		self.full_name = get_full_name(self.first_name, self.last_name)

	def on_trash(self):
		current_member = get_member_and_organization(frappe.session.user)[0]
		if current_member == self.name:
			frappe.throw(_("You cannot delete your own member record."))

		user = frappe.db.exists("User", {"landa_member": self.name})
		if user:
			frappe.delete_doc("User", user, ignore_permissions=True, ignore_missing=True, delete_permanently=True)

		delete_dynamically_linked("Address", self.doctype, self.name)
		delete_dynamically_linked("Contact", self.doctype, self.name)
		delete_records_linked_to("LANDA Member", self.name)

		self.revert_series()

	def revert_series(self):
		"""Decrease the naming counter when the newest member gets deleted."""
		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split('-')[-1])
		key = f"{self.name[:-number_part_len]}.{'#' * number_part_len}"
		revert_series_if_last(key, self.name)


def get_full_name(first_name,last_name):
	return (first_name or "") + (" " if (last_name and first_name) else "") + (last_name or "") 
