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
		fish_catches = self.fish_catches
		for i in range(len(fish_catches)):
			fish_species = frappe.get_doc('Fish Species', fish_catches[i].fish_species)
			if fish_catches[i].weight_in_kg < fish_species.typical_weight * 0.6 or fish_catches[i].weight_in_kg > fish_species.typical_weight * 1.4:
				frappe.msgprint("Das Gewicht des Fisches " + str(fish_catches[i].fish_species) + " in Zeile " + str(i + 1) + "  ist nicht plausibel")
        
        
