# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address

class Member(Document):

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
		except frappe.DuplicateEntryError:
			frappe.clear_messages()
