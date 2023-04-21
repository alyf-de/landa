# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CatchLogEntry(Document):
	def before_insert(self):
		user_roles = set(frappe.get_roles(frappe.session.user))
		regional_origin = {
			"LANDA Regional Organization Management",
			"LANDA Regional Water Body Management",
			"LANDA State Organization Employee",
			"System Manager",
			"Administrator",
		}
		if regional_origin.intersection(user_roles):
			self.origin_of_catch_log_entry = "Regionalverband"
		else:
			self.origin_of_catch_log_entry = "Verein"

	def validate(self):
		tolerance = 0.4
		for row in self.fish_catches:
			typical_weight = flt(frappe.db.get_value("Fish Species", row.fish_species, "typical_weight_in_kg"))
			average_weight = row.weight_in_kg / row.amount
			if (
				typical_weight and
				average_weight < typical_weight * (1 - tolerance) or
				average_weight > typical_weight * (1 + tolerance)
			):
				frappe.msgprint(
					frappe._("The weight of {0} in row {1} is not plausible").format(row.fish_species, row.idx)
				)