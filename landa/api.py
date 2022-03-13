from typing import Dict, List
import json
import frappe


@frappe.whitelist()
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
	
	return organizations
