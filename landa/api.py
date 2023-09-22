import json
from typing import Dict, List

import frappe

from landa.water_body_management.doctype.fish_species.fish_species import get_fish_species_data
from landa.water_body_management.doctype.water_body.water_body import (
	build_water_body_cache,
	build_water_body_data,
)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def organization(id: str = None) -> List[Dict]:
	filters = []
	if id and isinstance(id, str):
		filters.append(["Organization", "name", "like", id])

	organizations = frappe.get_all(
		"Organization",
		filters=filters,
		fields=[
			"name as id",
			"organization_name",
			"fishing_area",
			"website",
			"register_number",
			"location",
			"public_contact",
			"public_address",
		],
	)

	for organization in organizations:
		public_contact = organization.pop("public_contact")
		if public_contact:
			organization["contact"] = frappe.db.get_value(
				"Contact",
				public_contact,
				fieldname=[
					"salutation",
					"first_name",
					"middle_name",
					"last_name",
					"email_id as email",
					"mobile_no",
					"phone as phone_no",
				],
				as_dict=True,
			)

		public_address = organization.pop("public_address")
		if public_address:
			organization["address"] = frappe.db.get_value(
				"Address",
				public_address,
				fieldname=["address_line1", "address_line2", "pincode", "city"],
				as_dict=True,
			)

		location = organization.pop("location")
		if location:
			organization["geojson"] = json.loads(location)

		fishing_area = organization.pop("fishing_area")
		if fishing_area:
			organization["fishing_area"] = frappe.db.get_value(
				"Fishing Area",
				fishing_area,
				fieldname=["name as id", "area_name", "organization"],
				as_dict=True,
			)

	return organizations


@frappe.whitelist(allow_guest=True, methods=["GET"])
def water_body(id: str = None, fishing_area: str = None) -> List[Dict]:
	"""Return a list of water bodies with fish species and special provisions."""
	if id:
		# We do not cache ID since it's uniqueness makes the API performant
		return build_water_body_data(id, fishing_area)

	key = fishing_area or "all"
	cache_exists = frappe.cache().hexists("water_body_data", key)

	if not cache_exists:
		# Build the cache (for future calls)
		build_water_body_cache(fishing_area)

	# return the cached result
	return get_water_body_cache(key)


def get_water_body_cache(key: str) -> List[Dict]:
	"""Return a **CACHED** list of water bodies with fish species and special provisions."""
	return frappe.cache().hget("water_body_data", key)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def fish_species(id: str = None):
	"""Return a **CACHED** list of fish species. Uncached if ID is passed."""
	return get_fish_species_data(id)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def legal():
	"""Return water body rules in rich text format."""
	rules = frappe.get_single("Water Body Rules")
	return {
		"water_body_rules": rules.water_body_rules,
		"privacy_policy": rules.privacy_policy,
		"imprint": rules.imprint,
	}
