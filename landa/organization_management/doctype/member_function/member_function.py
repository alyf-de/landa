# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe

from frappe import _
from frappe.utils.data import today
from frappe.utils.data import date_diff
from frappe.model.document import Document


class MemberFunction(Document):
	def before_validate(self):
		self.update_is_active()

	def validate(self):
		if self.start_date and self.end_date:
			if date_diff(self.start_date, self.end_date) > 0:
				frappe.throw(_("End Date cannot be before Start Date."))

		self.validate_member_function_category()

	def validate_member_function_category(self):
		def has_role(role):
			return role in frappe.get_roles(frappe.session.user)

		access_level = frappe.get_value(
			"Member Function Category", self.member_function_category, "access_level"
		)

		if access_level == "Local Group":
			return

		if access_level == "State Organization" and has_role(
			"LANDA State Organization Employee"
		):
			return

		if access_level == "Regional Organization" and (
			has_role("LANDA State Organization Employee")
			or has_role("LANDA Regional Organization Management")
		):
			return

		if access_level == "Local Organization" and (
			has_role("LANDA State Organization Employee")
			or has_role("LANDA Regional Organization Management")
			or has_role("LANDA Local Organization Management")
		):
			return

		frappe.throw(
			_("No permission to set Member Function Category {0}").format(
				self.member_function_category
			),
			frappe.PermissionError,
		)

	def on_update(self):
		self.update_user_roles()

	def on_trash(self):
		self.status = "Inactive"
		self.update_user_roles()

	def update_user_roles(self):
		member_function_category = frappe.get_doc(
			"Member Function Category", self.member_function_category
		)
		if self.status == "Active":
			member_function_category.add_roles_and_permissions(self.member)
		else:
			member_function_category.remove_roles_and_permissions(
				self.member, disabled_member_function=self.name
			)

	def update_is_active(self):
		if self.is_planned():
			self.status = "Planned"
		elif self.is_inactive():
			self.status = "Inactive"
		else:
			self.status = "Active"

	def is_planned(self):
		return self.start_date and date_diff(today(), self.start_date) < 0

	def is_inactive(self):
		return self.end_date and date_diff(today(), self.end_date) > 0


def disable_expired_member_functions():
	for member_function in get_expired_member_functions():
		doc = frappe.get_doc("Member Function", member_function.name)
		doc.save()


def apply_active_member_functions(filters):
	for member_function in get_active_member_functions(filters=filters, pluck="name"):
		doc = frappe.get_doc("Member Function", member_function)
		doc.save()


def get_expired_member_functions():
	return frappe.get_all(
		"Member Function",
		filters=[
			["end_date", "<", today()],
			["end_date", "is", "set"],
		],
	)


def get_active_member_functions(filters: dict = None, pluck: str = None):
	return frappe.get_all(
		"Member Function",
		filters=filters,
		or_filters=[["end_date", "is", "not set"], ["end_date", ">=", today()]],
		pluck=pluck,
	)
