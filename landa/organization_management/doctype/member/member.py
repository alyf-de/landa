# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.contacts.address_and_contact import delete_contact_and_address
from frappe.model.naming import make_autoname
from frappe.model.naming import revert_series_if_last
from frappe.permissions import add_user_permission

from landa.organization_management.doctype.member_function.member_function import apply_active_member_functions
from landa.organization_management.doctype.member_function_category.member_function_category import get_highest_access_level

class Member(Document):
	
	def autoname(self):
		"""Generate the unique member number (name field)

		Organization:				AVL-001-0001, AVE-001-0001, ...
		Local group:				AVL-001-01-0001, AVL-001-02-0001, ...
		"""
		if self.name:
			return

		self.name = make_autoname(self.organization + '-.####', 'Member')

	def onload(self):
		load_address_and_contact(self)

	def validate(self):
		organization_is_group = lambda: frappe.db.get_value('Organization', self.organization, 'is_group')

		if organization_is_group():
			frappe.throw(_('Cannot be a member of organization {} because it is a group.').format(self.organization))

	def on_update(self):
		if self.user and self.has_value_changed('user'):
			self.create_user_permissions()
			apply_active_member_functions({'member': self.name})

	def on_trash(self):
		delete_contact_and_address(self.doctype, self.name)
		self.revert_series()

	def create_user_permissions(self):
		"""Restrict Member to itself and it's Organization."""
		add_user_permission('Member', self.name, self.user)
		add_user_permission('Organization', self.organization, self.user)

	def revert_series(self):
		"""Decrease the naming counter when the newest member gets deleted."""
		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split('-')[-1])
		key = self.name[:-number_part_len] + '.' + '#' * number_part_len

		revert_series_if_last(key, self.name)


@frappe.whitelist()
def belongs_to_parent_organization():
	"""Return True if session user belongs to a parent organization (Regionalverband) or no organization at all."""
	member_name = frappe.get_value('Member', {'user': frappe.session.user}, 'name')

	if member_name:
		access_level = get_highest_access_level(member_name)
		return access_level < 2

	return True
