# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt
from typing import Dict, List

import frappe
from frappe.model.document import Document
from frappe.utils.data import get_url


class FishSpecies(Document):
	pass


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
