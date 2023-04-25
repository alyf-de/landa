# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import List

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils.data import flt


class CatchLogFishTable(Document):
	def validate_weight(self):
		tolerance = 0.4
		typical_weight = flt(
			frappe.db.get_value("Fish Species", self.fish_species, "typical_weight_in_kg")
		)
		average_weight = self.weight_in_kg / self.amount
		if not typical_weight or (
			average_weight > typical_weight * (1 - tolerance)
			and average_weight < typical_weight * (1 + tolerance)
		):
			return True

		msgprint(
			_("The weight of {0} in row {1} diverges from the typical weight by more than 40 %").format(
				self.fish_species, self.idx
			),
			indicator="orange",
			alert=True,
		)
		return False

	def validate_species(self, main_species: List[str]):
		if self.fish_species in main_species:
			return True

		msgprint(
			_("The fish species {0} in row {1} is not a main species of the water body").format(
				self.fish_species, self.idx
			),
			indicator="orange",
			alert=True,
		)
		return False
