# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe

from landa.water_body_management.stocking_controller import StockingController


class StockingMeasure(StockingController):
	def on_change(self):
		self.update_stocking_target()

	def update_stocking_target(self):
		if not self.stocking_target:
			return

		frappe.get_doc("Stocking Target", self.stocking_target).update_status()
