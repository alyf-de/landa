# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import get_doc, get_roles
from frappe.model.document import Document


class CatchLogEntry(Document):
	def before_insert(self):
		user_roles = set(get_roles(frappe.session.user))
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
		water_body = get_doc("Water Body", self.water_body)
		main_species = [row.fish_species for row in water_body.fish_species]
		for row in self.fish_catches:
			row.plausible = int(row.validate_species(main_species) and row.validate_weight())
