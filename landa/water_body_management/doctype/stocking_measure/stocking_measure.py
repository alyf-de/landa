# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe

from landa.water_body_management.stocking_controller import StockingController


class StockingMeasure(StockingController):
	def after_insert(self):
		self.update_stocking_target()

	def update_stocking_target(self):
		"""Set status of Stocking Target to In Progress"""
		stocking_target = frappe.get_doc("Stocking Target", self.stocking_target)
		if stocking_target and stocking_target.status == "Draft":
			stocking_target.status = "In Progress"
			stocking_target.save()
