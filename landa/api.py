import json
from typing import Dict, List

import frappe


@frappe.whitelist(allow_guest=True)
def organization(id: str = None) -> List[Dict]:
	filters = []
	if id:
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
