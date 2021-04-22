# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet
from frappe.desk.treeview import make_tree_args
from frappe.model.naming import make_autoname
from frappe.model.naming import revert_series_if_last
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.contacts.address_and_contact import delete_contact_and_address

class Organization(NestedSet):
	nsm_parent_field = 'parent_organization'

	def autoname(self):
		"""Generate the unique organization number (name field)

		Top-Level-Organization:		according to short code (LVSA, AVL, AVE, ...)
		Organization:				AVL-001, AVE-001, ...
		Local group:				AVL-001-01, AVL-001-02, ...
		"""
		if self.name:
			return

		if self.is_top_level():
			# Landesverband oder Regionalverband
			self.name = self.short_code
		elif len(self.parent_organization) <= 4:
			# Organizations, parent_organization ist nach short_code benannt
			self.name = make_autoname(self.parent_organization + '-.###', 'Organization')
		else:
			# Local groups
			self.name = make_autoname(self.parent_organization + '-.##', 'Organization')

	def onload(self):
		load_address_and_contact(self)

	def on_update(self):
		NestedSet.on_update(self)

	def on_trash(self):
		NestedSet.validate_if_child_exists(self)
		frappe.utils.nestedset.update_nsm(self)
		delete_contact_and_address(self.doctype, self.name)
		self.revert_series()

	def is_top_level(self):
		"""Return true if I am the root organization or my parent is the root."""
		parent_is_root = lambda: not frappe.db.get_value('Organization', self.parent_organization, 'parent_organization')
		return not self.parent_organization or parent_is_root()

	def revert_series(self):
		"""Decrease the naming counter when the newest organization gets deleted."""
		if self.is_top_level():
			return

		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split('-')[-1])
		key = self.name[:-number_part_len] + '.' + '#' * number_part_len

		revert_series_if_last(key, self.name)


@frappe.whitelist()
def get_children(doctype, parent=None, organization=None, is_root=False):
	if parent == None or parent == "All Organizations":
		parent = ""

	return frappe.db.get_all(doctype, fields=[
			'name as value',
			'organization_name as title',
			'is_group as expandable'
		],
		filters={
			'parent_organization': parent
		}
	)


@frappe.whitelist()
def add_node():
	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_organization == 'All Organizations':
		args.parent_organization = None

	frappe.get_doc(args).insert()
