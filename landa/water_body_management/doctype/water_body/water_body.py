# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt
from typing import Dict, List

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import today

from landa.utils import get_current_member_data


class WaterBody(Document):
	def on_update(self):
		self.rebuild_water_body_cache()

	def on_trash(self):
		self.rebuild_water_body_cache()

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
					title=_("Invalid Species"),
				)

	def rebuild_water_body_cache(self):
		# Invalidate Cache
		frappe.cache().hdel("water_body_data", "all")
		frappe.cache().hdel("water_body_data", self.fishing_area)

		# Build Cache for all water bodies and fishing area wise
		build_water_body_cache()
		build_water_body_cache(fishing_area=self.fishing_area)


def remove_outdated_information():
	for name in frappe.get_all(
		"Water Body",
		filters=[
			["current_information_expires_on", "is", "set"],
			["current_information_expires_on", "<=", today()],
		],
		pluck="name",
	):
		water_body = frappe.get_doc("Water Body", name)
		water_body.current_public_information = None
		water_body.current_information_expires_on = None
		water_body.save()


def build_water_body_cache(fishing_area: str = None):
	"""Build the water body cache for all water bodies **OR** fishing area wise."""
	water_bodies = build_water_body_data(fishing_area=fishing_area)
	frappe.cache().hset("water_body_data", fishing_area, water_bodies)


def build_water_body_data(id: str = None, fishing_area: str = None) -> List[Dict]:
	"""Return a list of water bodies with fish species and special provisions."""
	filters = [
		["Water Body", "is_active", "=", 1],
		["Water Body", "display_in_fishing_guide", "=", 1],
	]
	if id and isinstance(id, str):
		filters.append(["Water Body", "name", "=", id])

	if fishing_area and isinstance(fishing_area, str):
		filters.append(["Water Body", "fishing_area", "=", fishing_area])

	water_bodies = frappe.get_all(
		"Water Body",
		filters=filters,
		fields=[
			"name as id",
			"title",
			"fishing_area",
			"fishing_area_name",
			"organization",
			"organization_name",
			"has_master_key_system",
			"guest_passes_available",
			"general_public_information",
			"current_public_information",
			"water_body_size as size",
			"water_body_size_unit as size_unit",
			"location",
		],
	)

	for water_body in water_bodies:
		water_body["fish_species"] = frappe.get_all(
			"Fish Species Table",
			filters={"parent": water_body["id"]},
			pluck="fish_species",
		)

		water_body["special_provisions"] = frappe.get_all(
			"Water Body Special Provision Table",
			filters={"parent": water_body["id"]},
			fields=["water_body_special_provision as id", "short_code"],
		)

		water_body["organizations"] = frappe.get_all(
			"Water Body Management Local Organization",
			filters={"water_body": water_body["id"]},
			fields=["organization as id", "organization_name"],
		)

		if water_body.location:
			water_body["geojson"] = frappe.parse_json(water_body.location)

	return water_bodies
