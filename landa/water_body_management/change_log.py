import json

import frappe
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import cint


class ChangeLog:
	def get_logs(self, from_datetime: str):
		"""
		Get queried and formatted change logs.
		"""
		self.changed_data = self._get_changed_data(from_datetime) or []
		return self._get_formatted_changes()

	def _get_changed_data(self, from_datetime: str):
		"""
		Get created, modified and deleted Water Body, Fish Species, WBMLO, Attached File data.
		"""
		created_modified = self._get_version_log_query(from_datetime)
		deleted = self._get_deleted_document_query(from_datetime)
		union_query = created_modified.union(deleted)
		return (frappe.qb.from_(union_query).select(union_query.star).orderby(union_query.creation)).run(
			as_dict=True
		)

	def _get_formatted_changes(self):
		"""
		Format changes dict to be displayed in the Change Log API.
		"""
		changes = []
		for entry in self.changed_data:
			change_log = self.format_change(entry)
			if change_log:
				changes.append(change_log)

		return changes

	def format_change(self, entry: dict):
		changed_data = frappe._dict(json.loads(entry.data))
		event = self._get_event(entry, changed_data)

		# Modified dependencies (File and WBMLO)
		if entry.doctype in ("File", "Water Body Management Local Organization"):
			return self._build_dependency_change_log(entry, changed_data)

		# Created/Deleted Water Body/Fish Species
		if event in ("Created", "Deleted"):
			return {
				"id": entry.name,
				"doctype": entry.doctype,
				"docname": entry.docname,
				"event": event,
				"datetime": entry.creation,
			}

		# Modified Water Body/Fish Species Log
		return self._build_modified_change_log(entry, changed_data, event)

	def _get_version_log_query(self, from_datetime: str):
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
						"Water Body Rules",
					]
				)
			)
			.where((file.attached_to_doctype.isnull()) | (file.attached_to_doctype == "Water Body"))
		)

	def _get_deleted_document_query(self, from_datetime: str):
		# Deleted Document DocType is not joined with File DocType
		# because the file does not exist anymore
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

	def _get_event(self, entry, changed_data):
		"""Return the event of the document (Created, Modified, Deleted)."""
		if cint(entry.deleted):
			return "Deleted"

		return "Created" if changed_data.updater_reference else "Modified"

	def _build_modified_change_log(self, entry, changed_data, event):
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
			key, data = row[0], row[2]

			# Newlines have been converted to <br> in the Version log
			# Convert them back to newlines for consistency with the other endpoints
			if frappe.get_meta(entry.doctype).get_field(key).fieldtype in ("Text", "Small Text"):
				data = data.replace("<br>", "\n")

			if row[0] == "location":
				key = "geojson"
				data = json.loads(row[2]) if row[2] else None

			change_log["changes"][key] = data

		return change_log

	def _build_dependency_change_log(self, entry, changed_data):
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
			return None

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
			ref_water_body = (
				changed_data.attached_to_name if cint(entry.deleted) else entry.attached_to_name
			)

		key = "files" if entry.doctype == "File" else "organizations"
		return {
			"id": entry.name,
			"doctype": "Water Body",
			"docname": ref_water_body,
			"event": "Modified",
			"datetime": entry.creation,
			"changes": {key: None},
		}
