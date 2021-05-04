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
		if self.user and self.create_user_permission:
			self.create_user_permissions()

	def on_trash(self):
		delete_contact_and_address(self.doctype, self.name)
		self.revert_series()

	def create_user_permissions(self):
		"""Restrict Member to itself and it's Organization."""
		try:
			frappe.get_doc(dict(
				doctype='User Permission',
				user=self.user,
				allow='Member',
				for_value=self.name
			)).insert()

			frappe.get_doc(dict(
				doctype='User Permission',
				user=self.user,
				allow='Organization',
				for_value=self.organization
			)).insert()

			frappe.get_doc(dict(
				doctype='User Permission',
				user=self.user,
				allow='Customer',
				for_value=frappe.get_value('Organization', self.organization, 'customer')
			)).insert()

		except frappe.DuplicateEntryError:
			frappe.clear_messages()

	def revert_series(self):
		"""Decrease the naming counter when the newest member gets deleted."""
		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split('-')[-1])
		key = self.name[:-number_part_len] + '.' + '#' * number_part_len

		revert_series_if_last(key, self.name)

@frappe.whitelist()
def belongs_to_parent_organization():
	"""Return True if session user belongs to a parent organization (Regionalverband) or no organization at all."""
	member = frappe.get_list('Member', filters={'user': frappe.session.user})
	
	if member:
		member_functions = frappe.get_list('Member Function',
			filters={
				'member': member[0].name
			},
			fields = ['member_function_category', 'is_active']
		)

		for member_function in member_functions:
			if member_function.is_active and frappe.get_value(
				'Member Function Category',
				member_function.member_function_category,
				'belongs_to_parent_organization'
			):
				return True
	else:
		return True

	return False


def get_user(member_name):
	"""Return the user object that belongs to this member."""
	user_name = frappe.get_value('Member', member_name, 'user')
	if user_name:
		return frappe.get_doc('User', user_name)
	else:
		return None
