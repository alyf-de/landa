# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document

from landa.utils import get_current_member_data


class WaterBody(Document):
	def validate(self):
		self.validate_edit_access()
		self.validate_blacklisted_fish_species()

	def validate_edit_access(self):
		current_member_data = get_current_member_data()
		if current_member_data.regional_organization and (
			self.organization != current_member_data.regional_organization
		):
			frappe.throw(_("You can only edit a Water Body if it belongs to your regional Organization."))

	def validate_blacklisted_fish_species(self):
		allowed_fish = [row.get("fish_species") for row in self.fish_species]

		for row in self.blacklisted_fish_species:
			fish_species = row.get("fish_species")
			if fish_species in allowed_fish:
				frappe.throw(
					_("Blacklisted Fish Species {0} cannot also be a Main Fish Species.").format(
						frappe.bold(fish_species)
					),
					title=_("Invalid Species")
				)
