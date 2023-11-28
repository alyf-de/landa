import json
from typing import List

import frappe
from frappe import _
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import cint


def create_version_log(doc, event):
	"""Called via hooks.py to create Version Log of document creation"""
	if doc.doctype == "File" and (doc.attached_to_doctype != "Water Body" or doc.is_private):
		return

	doc.flags.updater_reference = {
		"doctype": doc.doctype,
		"docname": doc.name,
		"event": "Created",
		"label": _("{0} {1} Created").format(doc.doctype, doc.name),
	}

	doc._doc_before_save = None


def get_changed_data(from_datetime: str):
	"""
	Get created, modified and deleted Water Body, Fish Species, WBMLO, Attached File data.
	"""
	created_modified = get_version_log_query(from_datetime)
	deleted = get_deleted_document_query(from_datetime)
	union_query = created_modified.union(deleted)
	return (frappe.qb.from_(union_query).select(union_query.star).orderby(union_query.creation)).run(
		as_dict=True
	)


def get_formatted_changes(changes_list: List):
	"""
	Format changes dict to be displayed in the Change Log API.
	"""
	changes = []
	for entry in changes_list:
		changed_data = frappe._dict(json.loads(entry.data))
		event = get_event(entry, changed_data)

		# Modified dependencies (File and WBMLO)
		if entry.doctype in ["File", "Water Body Management Local Organization"]:
			change_log = build_dependency_change_log(entry, changed_data)
			if change_log:
				changes.append(change_log)

			continue

		# Created/Deleted Water Body/Fish Species
		if event in ["Created", "Deleted"]:
			changes.append(
				{
					"id": entry.name,
					"doctype": entry.doctype,
					"docname": entry.docname,
					"event": event,
					"datetime": entry.creation,
				}
			)
			continue

		# Modified Water Body/Fish Species Log
		change_log = build_modified_change_log(entry, changed_data, event)
		if change_log:
			changes.append(change_log)

	return changes


def get_version_log_query(from_datetime: str):
	version = frappe.qb.DocType("Version")
	file = frappe.qb.DocType("File")
	return (
		frappe.qb.from_(version)
		.left_join(file)
		.on((version.ref_doctype == "File") & (version.docname == file.name))
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
			version.creation >= from_datetime,
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
		.where((file.attached_to_doctype.isnull()) | (file.attached_to_doctype == "Water Body"))
	)


def get_deleted_document_query(from_datetime: str):
	deleted_document = frappe.qb.DocType("Deleted Document")
	return (
		frappe.qb.from_(deleted_document)
		.select(
			deleted_document.name,
			deleted_document.deleted_doctype.as_("doctype"),
			deleted_document.deleted_name.as_("docname"),
			deleted_document.creation,
			deleted_document.data,
			ConstantColumn(1).as_("deleted"),
			ConstantColumn("").as_("attached_to_doctype"),
			ConstantColumn("").as_("attached_to_name"),
		)
		.where(
			deleted_document.creation >= from_datetime,
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


def get_event(entry, changed_data):
	"""Return the event of the document (Created, Modified, Deleted)."""
	if cint(entry.deleted):
		return "Deleted"

	return "Created" if changed_data.updater_reference else "Modified"


def build_modified_change_log(entry, changed_data, event):
	"""Return a pretty dict with changes for modified Water Body/Fish Species."""
	change_log = {
		"id": entry.name,
		"doctype": entry.doctype,
		"docname": entry.docname,
		"datetime": entry.creation,
		"event": event,
		"changes": {},
	}

	if not changed_data:
		return None

	# Table fields changes
	for key in ["added", "removed", "row_changed"]:
		change_log["changes"].update(
			{row[0]: None for row in changed_data.get(key) if row[0] not in change_log["changes"]}
		)

	# Other fields changes
	for row in changed_data.get("changed"):
		key = "geojson" if row[0] == "location" else row[0]
		change_log["changes"].update({key: row[2]})

	return change_log


def build_dependency_change_log(entry, changed_data):
	"""
	Return a pretty dict with changes in dependencies (File and WBMLO).
	`entry` could be creation (Version), modification (Version) or deletion (Deleted Document) events.
	"""
	if (
		cint(entry.deleted)
		and entry.doctype == "File"
		and changed_data.attached_to_doctype != "Water Body"
	):
		# Filter deleted documents that are not attached to water body
		return []

	if entry.doctype == "Water Body Management Local Organization":
		if cint(entry.deleted):
			ref_water_body = changed_data.get("water_body")  # Deleted WBMLO
		else:
			ref_water_body = frappe.db.get_value(  # Created/Modified WBMLO
				"Water Body Management Local Organization",
				entry.docname,
				"water_body",
			)
	else:
		ref_water_body = changed_data.attached_to_name if cint(entry.deleted) else entry.attached_to_name

	key = "files" if entry.doctype == "File" else "organizations"
	return {
		"id": entry.name,
		"doctype": "Water Body",
		"docname": ref_water_body,
		"event": "Modified",
		"datetime": entry.creation,
		"changes": {key: None},
	}
