# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import today
from landa.organization_management.doctype.member.member import get_user
from landa.organization_management.doctype.member_function.member_function import get_active_member_functions

class MemberFunctionCategory(Document):

	def on_update(self):
		add_roles(
			member_names=self.get_member_names(),
			roles=self.get_roles()
		)

	def get_member_names(self):
		"""Return a list of members to whom this Member Function Category applies."""
		member_names = get_active_member_functions(
			filters={
				'member_function_category': self.name
			},
			pluck='member'
		)

		return list(set(member_names))

	def get_roles(self):
		return [role.role for role in self.roles]

	def add_roles(self, member_name):
		"""Enable the roles of this Member Function Category for a specific Member."""
		add_roles([member_name], self.get_roles())

	def remove_roles(self, member_name, disabled_member_function):
		"""Disable the roles of this Member Function Category for a specific Member."""
		remove_roles(member_name, self.get_roles(), disabled_member_function)


def add_roles(member_names, roles):
	"""Add a list of roles to a list of members."""
	for member_name in member_names:
		user = get_user(member_name)
		if user:
			user.add_roles(*roles)


def remove_roles(member_name, roles, disabled_member_function):
	"""Remove a list of roles from a specific member.
	
	Keeps the roles from all active Member Functions into account, except from `disabled_member_function`.
	"""
	active_categories = get_active_member_functions(
		filters={
			'member': member_name,
			'name': ('!=', disabled_member_function)
		},
		pluck='member_function_category'
	)

	active_roles = frappe.get_all('Has Role', {
		'parenttype': 'Member Function Category',
		'parent': ('in', active_categories)
	}, pluck='role')

	active_categories = set(active_categories)
	active_roles = set(active_roles)

	roles_to_remove = list(roles - active_roles)
	user = get_user(member_name)

	if roles_to_remove and user:
		user.remove_roles(*roles_to_remove)
