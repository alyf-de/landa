# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class YearlyFishingPermit(Document):
	def before_insert(self):
		if not self.member:
			frappe.throw("Please select a LANDA Member")

	def validate(self):
		if self.member:
			self.first_name, self.last_name, self.organization = frappe.db.get_value(
				"LANDA Member", self.member, ["first_name", "last_name", "organization"]
			)

	def on_update(self):
		if self.has_permission("submit"):
			self.submit()
