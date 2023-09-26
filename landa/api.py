import json
from typing import Dict, List

import frappe
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import cint

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


@frappe.whitelist(allow_guest=True, methods=["GET"])
def change_log(from_datetime: str = None):
	"""Return a list of version logs of documents created/updated/deleted after the given datetime."""
	if not from_datetime:
		return []

	version = frappe.qb.DocType("Version")
	file = frappe.qb.DocType("File")
	created_modified = (
		frappe.qb.from_(version)
		.left_join(file)
		.on(version.docname == file.name)
		.select(
			version.name,
			version.ref_doctype.as_("doctype"),
			version.docname,
			version.creation,
			version.data,
			ConstantColumn(0).as_("deleted"),
			file.attached_to_doctype,
			file.attached_to_name,
		)
		.where(
			version.creation > from_datetime,
		)
		.where(
			version.ref_doctype.isin(
				[
					"Water Body",
					"Fish Species",
					"File",
					"Water Body Management Local Organization",
				]
			)
		)
		.where(file.attached_to_doctype.isnull() | file.attached_to_doctype == "Water Body")
	)

	deleted_document = frappe.qb.DocType("Deleted Document")
	deleted = (
		frappe.qb.from_(deleted_document)
		.select(
			deleted_document.name,
			deleted_document.deleted_doctype.as_("doctype"),
			deleted_document.deleted_name.as_("docname"),
			deleted_document.creation,
			deleted_document.data,
			ConstantColumn(1).as_("deleted"),
			ConstantColumn(None).as_("attached_to_doctype"),
			ConstantColumn(None).as_("attached_to_name"),
		)
		.where(
			deleted_document.creation > from_datetime,
		)
		.where(
			deleted_document.deleted_doctype.isin(
				[
					"Water Body",
					"Fish Species",
					"File",
					"Water Body Management Local Organization",
				]
			)
		)
	)

	union_qry = created_modified.union(deleted)
	result = (
		frappe.qb.from_(union_qry).select(union_qry.star).orderby(union_qry.creation).run(as_dict=True)
	)

	changes = []
	for entry in result:
		changed_data = frappe._dict(json.loads(entry.data))
		event = get_event(entry, changed_data)

		if entry.doctype in ["File", "Water Body Management Local Organization"]:
			change_log = log_dependency_change(entry, changed_data)
			if change_log:
				changes.append(change_log)

			continue

		if event in ["Created", "Deleted"]:
			changes.append(
				{
					"doctype": entry.doctype,
					"docname": entry.docname,
					"event": event,
					"datetime": entry.creation,
				}
			)
			continue

		# Modified Water Body/Fish Species Log
		change_log = {
			"doctype": entry.doctype,
			"docname": entry.docname,
			"datetime": entry.creation,
			"event": event,
			"changes": {},
		}

		if not changed_data:
			continue

		for key in ["added", "removed", "row_changed"]:
			change_log["changes"].update(
				{row[0]: None for row in changed_data.get(key) if row[0] not in change_log["changes"]}
			)

		change_log["changes"].update({row[0]: row[2] for row in changed_data.get("changed")})

		changes.append(change_log)

	return changes


def get_event(entry, changed_data):
	if cint(entry.deleted):
		return "Deleted"

	return "Modified" if not changed_data.updater_reference else "Created"


def log_dependency_change(entry, changed_data):
	if (
		cint(entry.deleted)
		and entry.doctype == "File"
		and changed_data.attached_to_doctype != "Water Body"
	):
		# Filter deleted documents that are not attached to water body
		return []

	if entry.doctype == "Water Body Management Local Organization":
		ref_water_body = frappe.db.get_value(
			"Water Body Management Local Organization",
			entry.docname,
			"water_body",
		)
	else:
		ref_water_body = entry.attached_to_name or changed_data.attached_to_name

	key = "files" if entry.doctype == "File" else "organizations"
	return {
		"doctype": "Water Body",
		"docname": ref_water_body,
		"event": "Modified",
		"datetime": entry.creation,
		"changes": {key: None},
	}
