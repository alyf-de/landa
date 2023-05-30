import json
from typing import Dict, List

import frappe


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
			"general_public_information",
			"current_public_information",
			"water_body_size as size",
			"water_body_size_unit as size_unit",
			"location",
		],
	)

	for water_body in water_bodies:
		fish_species = frappe.get_all(
			"Fish Species Table",
			filters={"parent": water_body["id"]},
			fields=["fish_species as id", "short_code"],
		)
		water_body["fish_species"] = fish_species

		special_provisions = frappe.get_all(
			"Water Body Special Provision Table",
			filters={"parent": water_body["id"]},
			fields=["water_body_special_provision as id", "short_code"],
		)
		water_body["special_provisions"] = special_provisions

		if water_body.location:
			water_body["geojson"] = json.loads(water_body.location)

	return water_bodies
