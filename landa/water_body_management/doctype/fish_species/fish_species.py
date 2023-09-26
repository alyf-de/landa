# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt
from typing import Dict, List

import frappe
from frappe.model.document import Document
from frappe.utils.data import get_url


class FishSpecies(Document):
	def on_update(self):
		build_fish_species_cache()

	def after_delete(self):
		build_fish_species_cache()

	def after_rename(self, old, new, merge):
		build_fish_species_cache()


def get_fish_species_data(id: str = None) -> List[Dict]:
	"""Return fish species from cache."""
	if id:
		# We do not cache ID since it's uniqueness makes the API performant
		return query_fish_species_data(id)

	cache_exists = frappe.cache().hexists("fish_species_data", "all")
	if not cache_exists:
		build_fish_species_cache()

	return frappe.cache().hget("fish_species_data", "all")


def build_fish_species_cache():
	"""Rebuild entire fish species data and set in cache."""
	frappe.cache().hset("fish_species_data", "all", query_fish_species_data())


def query_fish_species_data(id: str = None) -> List[Dict]:
	fish_species = frappe.qb.DocType("Fish Species")
	query = frappe.qb.from_(fish_species).select(
		fish_species.title.as_("id"),
		fish_species.short_code,
		fish_species.scientific_name,
		fish_species.close_season,
		fish_species.minimum_size,
		fish_species.general_fishing_limit,
		fish_species.special_fishing_limit,
		fish_species.traits,
		fish_species.wikipedia_link,
		fish_species.image,
		fish_species.thumbnail,
	)

	if id:
		query = query.where(fish_species.title == id)

	result = query.run(as_dict=True)

	if not result:
		return []

	for row in result:
		# images must be absolute URLs
		if row.image:
			row.image = get_url(row.image)
		if row.thumbnail:
			row.thumbnail = get_url(row.thumbnail)

	return result
