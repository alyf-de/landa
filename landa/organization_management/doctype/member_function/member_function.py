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
	member_functions = frappe.get_all('Member Function', {
		'end_date': ('<', today())
	})

	for member_function in member_functions:
		doc = frappe.get_doc("Member Function", member_function.name)
		doc.save()
