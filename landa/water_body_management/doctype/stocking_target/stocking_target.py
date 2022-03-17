# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import get_link_to_form


class StockingTarget(Document):
	def validate(self):
		existing_stocking_target = frappe.db.get_value(
			self.doctype,
			{
				"year": self.year,
				"water_body": self.water_body,
				"fish_species": self.fish_species,
				"fish_type_for_stocking": self.fish_type_for_stocking,
			},
		)
		if existing_stocking_target and existing_stocking_target != self.name:
			frappe.throw(
				_("Please update the existing record: {0}").format(
					get_link_to_form(self.doctype, existing_stocking_target)
				)
			)
