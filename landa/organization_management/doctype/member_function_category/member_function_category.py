# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from enum import Enum

import frappe
from frappe.model.document import Document
from frappe.utils.data import today
from frappe.permissions import add_user_permission
from landa.organization_management.doctype.member.member import get_user

class AccessLevel(Enum):
	STATE = 0
	REGION = 1
	CITY = 2

	@classmethod
	def get_lowest(cls):
		return cls(max(lvl.value for lvl in cls))


class MemberFunctionCategory(Document):

	def on_update(self):
		add_roles_and_permissions(
			member_names=self.get_member_names(),
			roles=self.get_roles(),
			access_level=self.get_access_level()
		)

	def get_member_names(self):
		"""Return a list of members to whom this Member Function Category applies."""
		member_names = frappe.get_all('Member Function',
			filters={
				'member_function_category': self.name
			},
			or_filters=[
				['end_date', 'is', 'not set'],
				['end_date', '>=', today()]
			],
			pluck='member'
		)

		return list(set(member_names))

	def get_roles(self):
		return [role.role for role in self.roles]

	def add_roles(self, member_name):
		"""Enable the roles of this Member Function Category for a specific Member."""
		add_roles_and_permissions(
			member_names=[member_name],
			roles=self.get_roles(),
			level_name=self.get_access_level()
		)

	def remove_roles(self, member_name, disabled_member_function):
		"""Disable the roles of this Member Function Category for a specific Member."""
		remove_roles(member_name, self.get_roles(), disabled_member_function)

	def get_access_level(self):
		return AccessLevel[self.access_level.upper()] if self.access_level else AccessLevel.get_lowest()


def add_roles_and_permissions(member_names: str, roles: list, access_level: str):
	"""Add a list of roles to a list of members."""
	for member_name in member_names:
		user = get_user(member_name)
		organization = None
		highest_access_level = None

		if access_level:
			highest_access_level = get_highest_access_level(member_name)
			organization_name = get_organization(member_name, access_level)

		if user:
			user.add_roles(*roles)
			if organization_name and highest_access_level.value > access_level.value:
				delete_existing_permission(user.name, 'Organization')
				add_user_permission('Organization', organization_name, user.name, ignore_permissions=True)


def remove_roles(member_name: str, roles: list, disabled_member_function: str):
	"""Remove a list of roles from a specific member.

	Keeps the roles from all active Member Functions into account, except from `disabled_member_function`.
	"""
	active_categories = frappe.get_all('Member Function', {
		'end_date': ('>=', today()),
		'member': member_name,
		'name': ('!=', disabled_member_function)
	}, pluck='member_function_category')

	active_roles = frappe.get_all('Has Role', {
		'parenttype': 'Member Function Category',
		'parent': ('in', active_categories)
	}, pluck='role')

	roles_to_remove = list(set(roles).difference(set(active_roles)))
	user = get_user(member_name)

	if roles_to_remove and user:
		user.remove_roles(*roles_to_remove)


def get_organization(member_name: str, access_level: AccessLevel):
	"""Get the member's organization at a given level in the tree."""
	organization_name = frappe.get_value('Member', member_name, 'organization')
	organization = frappe.get_doc('Organization', organization_name)
	ancestors = organization.get_ancestors()
	ancestors.reverse() # root as the first element

	return ancestors[access_level.value]


def get_highest_access_level(member_name: str):
	"""Return the highest AccessLevel needed for member's functions."""
	active_categories = frappe.get_all('Member Function', {
		'end_date': ('>=', today()),
		'member': member_name
	}, pluck='member_function_category')

	access_levels = frappe.get_all('Member Function Category', {
		'name': ('in', active_categories),
		'access_level': ('is', 'set')
	}, pluck='access_level')

	min_level = AccessLevel.get_lowest()
	if access_levels:
		min_level = min((AccessLevel[level.upper()] for level in access_levels), key=lambda level: level.value)

	return min_level


def delete_existing_permission(user_name: str, doctype: str):
	"""Delete any existing User Permissions for user_name on doctype."""
	existing_permission = frappe.db.exists('User Permission', {'user': user_name, 'allow': doctype})
	if existing_permission:
		frappe.delete_doc('User Permission', existing_permission)
