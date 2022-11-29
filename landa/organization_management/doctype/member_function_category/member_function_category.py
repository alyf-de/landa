# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.permissions import add_user_permission

from landa.organization_management.doctype.member_function.member_function import get_active_member_functions


class MemberFunctionCategory(Document):

	def on_update(self):
		if self.has_value_changed('roles'):
			member_names = self.get_member_names()
			remove_roles(member_names, self.get_removed_roles())
			add_roles(member_names, self.get_new_roles())

		if self.has_value_changed('member_administration'):
			update_member_restrictions(self.get_member_names())

		if self.has_value_changed('access_level'):
			update_organization_restrictions(self.get_member_names())

	def get_member_names(self):
		"""Return a list of members to whom this Member Function Category applies."""
		filters = {'member_function_category': self.name}
		member_names = get_active_member_functions(filters=filters, pluck='member')

		return list(set(member_names))

	def get_removed_roles(self):
		doc_before_save = self.get_doc_before_save()

		if doc_before_save:
			return list(set(role.role for role in doc_before_save.roles) - set(role.role for role in self.roles))
		else:
			return []

	def get_new_roles(self):
		doc_before_save = self.get_doc_before_save()

		if doc_before_save:
			return list(set(role.role for role in self.roles) - set(role.role for role in doc_before_save.roles))
		else:
			return self.get_roles()

	def get_roles(self):
		return [role.role for role in self.roles]

	def add_roles_and_permissions(self, member_name):
		"""Enable the roles of this Member Function Category for a specific Member."""
		add_roles_to_member(member_name, self.get_roles())
		update_user_permission_on_member(member_name)
		update_user_permission_on_organization(member_name)

	def remove_roles_and_permissions(self, member_name, disabled_member_function):
		"""Disable the roles of this Member Function Category for a specific Member."""
		remove_roles_from_member(member_name, self.get_roles(), disabled_member_function)
		update_user_permission_on_member(member_name, disabled_member_function)
		update_user_permission_on_organization(member_name, disabled_member_function)


def add_roles(member_names, roles):
	"""Add a list of roles to a list of members."""
	for member_name in member_names:
		add_roles_to_member(member_name, roles)


def remove_roles(member_names, roles):
	"""Remove a list of roles from a list of members."""
	for member_name in member_names:
		remove_roles_from_member(member_name, roles)


def update_member_restrictions(member_names):
	for member_name in member_names:
		update_user_permission_on_member(member_name)


def update_organization_restrictions(member_names):
	for member_name in member_names:
		update_user_permission_on_organization(member_name)


def add_roles_to_member(member_name, roles):
	"""Add a list of roles to a specific member."""
	user = get_user(member_name)
	if user:
		user.flags.ignore_permissions = 1
		user.add_roles(*roles)


def remove_roles_from_member(member_name, roles, disabled_member_function=None):
	"""Remove a list of roles from a specific member.

	Keeps the roles from all active Member Functions into account, except from `disabled_member_function`.
	"""
	roles_to_remove = get_roles_to_remove(member_name, roles, disabled_member_function)
	user = get_user(member_name)

	if roles_to_remove and user:
		user.flags.ignore_permissions = 1
		user.remove_roles(*roles_to_remove)


def update_user_permission_on_member(member_name, disabled_member_function=None):
	"""Remove the User Permission restricting member_name's User to it's own Member record."""
	user = get_user(member_name)
	if not user:
		return

	if is_member_administration(member_name, disabled_member_function):
		clear_user_permissions_for_doctype('LANDA Member', user.name, ignore_permissions=True)
	else:
		add_user_permission('LANDA Member', member_name, user.name, ignore_permissions=True)


def update_user_permission_on_organization(member_name, disabled_member_function=None):
	"""Give member_name's User access to Organization at the highest level needed for it's Member Functions."""
	user = get_user(member_name)
	if not user:
		return

	highest_access_level = get_highest_access_level(member_name, disabled_member_function)
	organization_name = get_organization_at_level(member_name, highest_access_level)

	clear_user_permissions_for_doctype('Organization', user.name, ignore_permissions=True)
	add_user_permission('Organization', organization_name, user.name, ignore_permissions=True)


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
	active_roles.add("LANDA Member")  # LANDA Member is always active
	roles = set(roles)

	return list(roles - active_roles)


def get_organization_at_level(member_name, access_level, organization_name=None):
	"""Get the member's organization at a given level in the tree."""
	if not organization_name:
		organization_name = frappe.get_value('LANDA Member', member_name, 'organization')

	organization = frappe.get_doc('Organization', organization_name)
	ancestors = organization.get_ancestors()
	ancestors.reverse() # root as the first element

	if access_level >= len(ancestors):
		return organization_name

	return ancestors[access_level]


def get_highest_access_level(member_name, disabled_member_function=None):
	"""Return the highest access level needed for member's functions."""
	ACCESS_LEVEL_MAP = {
		'State Organization': 0,
		'Regional Organization': 1,
		'Local Organization': 2,
		'Local Group': 3,
	}
	access_levels = get_values_from_categories(member_name, {'access_level': ('is', 'set')}, 'access_level', disabled_member_function)

	min_level = max(ACCESS_LEVEL_MAP.values())
	if access_levels:
		min_level = min((ACCESS_LEVEL_MAP[level] for level in access_levels))

	return min_level


def is_member_administration(member_name, disabled_member_function=None):
	member_administration = get_values_from_categories(member_name, {'member_administration': 1}, 'name', disabled_member_function)

	return bool(member_administration)


def get_values_from_categories(member_name, filters, fieldname=None, disabled_member_function=None):
	member_function_filters = {
		'member': member_name
	}

	if disabled_member_function:
		member_function_filters['name'] = ('!=', disabled_member_function)

	active_categories = get_active_member_functions(member_function_filters, pluck='member_function_category')
	filters['name'] = ('in', active_categories)

	return frappe.get_all('Member Function Category', {
		'name': ('in', active_categories),
		'member_administration': 1
	}, pluck=fieldname)


def get_user(member_name):
	"""Return the user object that belongs to this member."""
	user_name = frappe.get_value('LANDA Member', member_name, 'user')
	if user_name:
		return frappe.get_doc('User', user_name)
	else:
		return None


def clear_user_permissions_for_doctype(doctype, user=None, ignore_permissions=False):
	"""Copy of `frappe.permissions` with additional parameter `ignore_permissions`."""
	filters = {'allow': doctype}
	if user:
		filters['user'] = user
	user_permissions_for_doctype = frappe.db.get_all('User Permission', filters=filters)
	for d in user_permissions_for_doctype:
		frappe.delete_doc('User Permission', d.name, ignore_permissions=ignore_permissions)


def apply_roles(member_name: str) -> None:
	"""Apply roles from all active member functions to the member."""
	mfcs = get_active_member_functions(
		filters={'member': member_name},
		pluck='member_function_category'
	)
	roles = frappe.get_all(
		'Has Role',
		filters={'parenttype': 'Member Function Category', 'parent': ('in', mfcs)},
		pluck='role',
		distinct=True,
	)

	user = get_user(member_name)
	user.roles = []
	for role in set(roles + ['LANDA Member']):
		user.append('roles', {'role': role})
	user.save(ignore_permissions=True, ignore_version=True)
