# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt
from collections import defaultdict
from json import loads
from typing import Dict, List

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import get_url, today

from landa.utils import get_current_member_data


class WaterBody(Document):
	def on_update(self):
		rebuild_water_body_cache(self.fishing_area)

	def after_delete(self):
		rebuild_water_body_cache(self.fishing_area)

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


def rebuild_water_body_cache(fishing_area: str = None, enqueued: bool = False):
	"""
	Rebuilds water body cache for all water bodies **AND** fishing area wise.
	"""
	# Invalidate Cache
	if enqueued:
		frappe.cache().hset("water_body_data", "in_progress", 1)

	frappe.cache().hdel("water_body_data", "all")
	build_water_body_cache()

	if fishing_area:
		frappe.cache().hdel("water_body_data", fishing_area)
		build_water_body_cache(fishing_area=fishing_area)

	if enqueued:
		frappe.cache().hset("water_body_data", "in_progress", 0)


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
	"""
	Build the water body cache for all water bodies **OR** fishing area wise.
	"""
	water_bodies = build_water_body_data(fishing_area=fishing_area)
	key = fishing_area or "all"
	frappe.cache().hset("water_body_data", key, water_bodies)


def build_water_body_data(id: str = None, fishing_area: str = None) -> List[Dict]:
	"""
	Return a list of water bodies with fish species and special provisions
	"""
	result = query_water_body_data(id=id, fishing_area=fishing_area)
	return consolidate_water_body_data(water_body_data=result)


def query_water_body_data(id: str = None, fishing_area: str = None) -> List[Dict]:
	water_body = frappe.qb.DocType("Water Body")
	fish_species_table = frappe.qb.DocType("Fish Species Table")
	wb_provision_table = frappe.qb.DocType("Water Body Special Provision Table")
	wb_local_org_table = frappe.qb.DocType("Water Body Management Local Organization")

	query = (
		frappe.qb.from_(water_body)
		.left_join(fish_species_table)
		.on(fish_species_table.parent == water_body.name)
		.left_join(wb_provision_table)
		.on(wb_provision_table.parent == water_body.name)
		.left_join(wb_local_org_table)
		.on(wb_local_org_table.water_body == water_body.name)
		.select(
			water_body.name.as_("id"),
			water_body.title,
			water_body.fishing_area,
			water_body.fishing_area_name,
			water_body.organization,
			water_body.organization_name,
			water_body.has_master_key_system,
			water_body.guest_passes_available,
			water_body.general_public_information,
			water_body.current_public_information,
			water_body.water_body_size.as_("size"),
			water_body.water_body_size_unit.as_("size_unit"),
			water_body.location,
			water_body.status,
			fish_species_table.fish_species,
			wb_provision_table.water_body_special_provision,
			wb_provision_table.short_code,
			wb_local_org_table.organization.as_("local_organization"),
			wb_local_org_table.organization_name.as_("local_organization_name"),
		)
		.where(water_body.is_active == 1)
		.where(water_body.display_in_fishing_guide == 1)
	)

	if id and isinstance(id, str):
		query = query.where(water_body.name == id)

	if fishing_area and isinstance(fishing_area, str):
		query = query.where(water_body.fishing_area == fishing_area)

	return query.run(as_dict=True)


def consolidate_water_body_data(water_body_data: List[Dict]) -> List[Dict]:
	"""
	Deduplicate the water body data such that each water body has a list of unique
	fish species, special provisions and local organizations.
	"""
	water_body_map = {}  # {water_body_name: water_body_data}
	fish_species_map, provision_map, local_org_map = (
		defaultdict(list),
		defaultdict(list),
		defaultdict(list),
	)

	for entry in water_body_data:
		water_body_name = entry.get("id")
		if not water_body_name in water_body_map:
			# Add entry to map if it does not exist
			water_body_map[water_body_name] = init_row(water_body_row=entry)

		result_entry = water_body_map[water_body_name]

		# Add unique child table and Water Body Management Local Organization data
		fish_species = entry.get("fish_species")
		add_to_map(fish_species, "fish_species", entry, fish_species_map, result_entry)

		provision = entry.get("water_body_special_provision")
		add_to_map(provision, "special_provisions", entry, provision_map, result_entry)

		org = entry.get("local_organization")
		add_to_map(org, "organizations", entry, local_org_map, result_entry)

	return [water_body_map.get(key) for key in water_body_map]


def init_row(water_body_row: Dict) -> Dict:
	# Prepare row to have Water Body data (excluding child tables)
	water_body_copy = water_body_row.copy()
	location = water_body_copy.pop("location", None)

	if location and isinstance(location, str):
		water_body_copy["geojson"] = loads(location)

	for field in (
		"fish_species",
		"water_body_special_provision",
		"short_code",
		"local_organization",
		"local_organization_name",
	):
		water_body_copy.pop(field)  # Remove child table fields

	for field in ("fish_species", "special_provisions", "organizations"):
		# Re-insert child table fields as lists
		water_body_copy[field] = []

	water_body_copy["files"] = get_water_body_files(water_body_row.get("id"))
	return water_body_copy


def add_to_map(value, field, water_body, checking_map, result_map):
	"""
	Add the value to the `result_map` if it does not exist in the `checking_map`.
	Also update the `checking_map` with the value.
	"""
	water_body_name = water_body.get("id")
	checking_result_map = checking_map[water_body_name]

	if not value or (value in checking_result_map):
		return

	checking_result_map.append(value)

	if field == "fish_species":
		result_map[field].append(value)
	elif field == "special_provisions":
		result_map[field].append({"id": value, "short_code": water_body.get("short_code")})
	else:
		result_map[field].append(
			{"id": value, "organization_name": water_body.get("local_organization_name")}
		)


def get_water_body_files(water_body_id: str):
	file = frappe.qb.DocType("File")
	files = (
		frappe.qb.from_(file)
		.select(file.file_url)
		.where(file.attached_to_doctype == "Water Body")
		.where(file.attached_to_name == water_body_id)
		.where(file.is_private == 0)
	).run()

	return [get_url(file[0]) for file in files] if files else []


def rebuild_cache_on_attachment(doc, method):
	"""Called via hooks.py when a file is attached to/removed from a Water Body."""
	if not doc.attached_to_doctype == "Water Body":
		return

	if method == "on_update" and not doc.flags.in_insert:  # update
		if doc.get_doc_before_save().file_url == doc.file_url:
			# switching from public to private or vice versa, changes the URL
			# File URL has not changed, so no need to rebuild cache
			return
	elif doc.is_private:
		# Private files don't impact cache on insert/delete
		return

	water_body_data = frappe.db.get_value(
		"Water Body",
		doc.attached_to_name,
		["is_active", "display_in_fishing_guide", "fishing_area"],
		as_dict=True,
	)
	if not water_body_data:
		# Water Body has been deleted, cache rebuild is handled by water body
		return

	if not water_body_data.is_active or not water_body_data.display:
		return

	if method == "after_delete":
		# NOTE:Enqueue gets uncommitted data (new thread). Files appear even if deleted
		# Still no clue why
		rebuild_water_body_cache(fishing_area=water_body_data.fishing_area)
	elif not frappe.cache().hget("water_body_data", "in_progress"):
		frappe.enqueue(
			rebuild_water_body_cache,
			fishing_area=water_body_data.fishing_area,
			enqueued=True,
		)
