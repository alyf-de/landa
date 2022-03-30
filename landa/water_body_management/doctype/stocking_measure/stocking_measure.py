# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockingMeasure(Document):
	def after_insert(self):
		self.update_stocking_target()

	def update_stocking_target(self):
		"""Set status of Stocking Target to In Progress"""
		stocking_target = frappe.get_doc("Stocking Target", self.stocking_target)
		if stocking_target.status == "Draft":
			stocking_target.status = "In Progress"
			stocking_target.save()
