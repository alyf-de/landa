# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from landa.organization_management.doctype.member.member import get_user
from landa.organization_management.doctype.member_function.member_function import get_active_member_functions

class MemberFunctionCategory(Document):

	def on_update(self):
		if self.has_value_changed('roles'):
			member_names = self.get_member_names()

			remove_roles(member_names, self.get_removed_roles())
			add_roles(member_names, self.get_new_roles())

	def get_member_names(self):
		"""Return a list of members to whom this Member Function Category applies."""
		member_names = get_active_member_functions(
			filters={
				'member_function_category': self.name
			},
			pluck='member'
		)

		return list(set(member_names))

	def get_removed_roles(self):
		doc_before_save = self.get_doc_before_save()
		return list(set(role.role for role in doc_before_save.roles) - set(role.role for role in self.roles))

	def get_new_roles(self):
		doc_before_save = self.get_doc_before_save()
		return list(set(role.role for role in self.roles) - set(role.role for role in doc_before_save.roles))

	def get_roles(self):
		return [role.role for role in self.roles]

	def add_roles(self, member_name):
		"""Enable the roles of this Member Function Category for a specific Member."""
		add_roles_to_member(member_name, self.get_roles())

	def remove_roles(self, member_name, disabled_member_function):
		"""Disable the roles of this Member Function Category for a specific Member."""
		remove_roles_from_member(member_name, self.get_roles(), disabled_member_function)


def add_roles(member_names, roles):
	"""Add a list of roles to a list of members."""
	for member_name in member_names:
		add_roles_to_member(member_name, roles)


def remove_roles(member_names, roles):
	"""Remove a list of roles from a list of members."""
	for member_name in member_names:
		remove_roles_from_member(member_name, roles)


def add_roles_to_member(member_name, roles):
	"""Add a list of roles to a specific member."""
	user = get_user(member_name)
	if user:
		user.add_roles(*roles)


def remove_roles_from_member(member_name, roles, disabled_member_function=None):
	"""Remove a list of roles from a specific member.

	Keeps the roles from all active Member Functions into account, except from `disabled_member_function`.
	"""
	roles_to_remove = get_roles_to_remove(member_name, roles, disabled_member_function)
	user = get_user(member_name)

	if roles_to_remove and user:
		user.remove_roles(*roles_to_remove)


def get_roles_to_remove(member_name, roles, disabled_member_function=None):
	filters = {'member': member_name}

	if disabled_member_function:
		filters['name'] = ('!=', disabled_member_function)

	active_categories = get_active_member_functions(filters=filters, pluck='member_function_category')
	active_roles = frappe.get_all('Has Role', {
		'parenttype': 'Member Function Category',
		'parent': ('in', active_categories)
	}, pluck='role')

	active_roles = set(active_roles)
	roles = set(roles)

	return list(roles - active_roles)
