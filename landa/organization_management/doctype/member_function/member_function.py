# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe

from frappe.utils.data import today
from frappe.utils.data import date_diff
from frappe.model.document import Document

class MemberFunction(Document):

	def before_validate(self):
		self.update_is_active()

	def on_update(self):
		self.update_user_roles()

	def update_user_roles(self):
		member_function_category = frappe.get_doc("Member Function Category", self.member_function_category)
		if self.is_active:
			member_function_category.add_roles(self.member)
		else:
			member_function_category.remove_roles(self.member, disabled_member_function=self.name)

	def update_is_active(self):
		if self.end_date:
			self.is_active = date_diff(today(), self.end_date) < 0
		else:
			self.is_active = True


def disable_expired_member_functions():
	for member_function in get_expired_member_functions():
		doc = frappe.get_doc("Member Function", member_function.name)
		doc.save()


def get_expired_member_functions():
	return frappe.get_all('Member Function', filters=[
		['end_date', '<', today()],
		['end_date', 'is', 'set'],
	])


def get_active_member_functions(filters: dict=None, pluck: str=None):
	return frappe.get_all('Member Function',
		filters=filters,
		or_filters=[
			['end_date', 'is', 'not set'],
			['end_date', '>=', today()]
		],
		pluck=pluck
	)
