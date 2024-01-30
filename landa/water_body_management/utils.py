import json

import frappe
from frappe import _

from landa.firebase_connector import FirebaseNotification
from landa.water_body_management.change_log import ChangeLog

VALID_DOCTYPES = [
	"Water Body",
	"Fish Species",
	"File",
	"Water Body Management Local Organization",
	"Water Body Rules",
]


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


def create_firebase_notification(doc, event):
	"""Enqueue this on hooks.py to send firebase notification on doc event"""
	if frappe.flags.in_test or frappe.flags.in_patch or frappe.flags.in_install:
		return

	if not doc_eligible(doc):
		return

	firebase_settings = frappe.get_single("Firebase Settings")
	if not firebase_settings.enable_firebase_notifications or not firebase_settings.has_credentials:
		return

	# doc must have keys same as `ChangeLog()._get_changed_data` query
	# Important: create a copy of the doc (via as_dict) before modifying, in
	# order to not update the existing doc.
	formatted_doc = format_doc_for_change_log(doc.as_dict())
	change_log = ChangeLog().format_change(formatted_doc)
	if not change_log:
		return

	# firebase doesn't allow nested objects
	change_log["changes"] = json.dumps(change_log["changes"])

	# Send notification to topic
	frappe.enqueue(
		send_firebase_notification,
		queue="default",
		file_path=firebase_settings.credentials_path,
		project_id=firebase_settings.project_id,
		topic=firebase_settings.firebase_topic,
		change_log=change_log,
		now=frappe.conf.developer_mode,
	)


def send_firebase_notification(file_path, project_id, topic, change_log):
	try:
		fcm = FirebaseNotification(file_path, project_id)
		fcm.send_to_topic(topic, change_log)
	except Exception:
		frappe.log_error(
			message=frappe.get_traceback(),
			title=_("Firebase Notification Error"),
		)


def doc_eligible(doc):
	"""
	Check if document is eligible for firebase notification
	"""
	if doc.doctype == "Version":
		if doc.ref_doctype not in VALID_DOCTYPES:
			return False

		if doc.ref_doctype == "File":
			return frappe.db.get_value("File", doc.docname, "attached_to_doctype") == "Water Body"

		return True

	if doc.doctype == "Deleted Document":
		return doc.deleted_doctype in VALID_DOCTYPES[:-1]

	return False


def format_doc_for_change_log(doc):
	"""Format doc for change log"""
	doc.attached_to_name = None

	if doc.doctype == "Version":
		if doc.ref_doctype == "File":
			doc.attached_to_name = frappe.db.get_value("File", doc.docname, "attached_to_name")
		doc.doctype = doc.ref_doctype
		doc.deleted = 0
	elif doc.doctype == "Deleted Document":
		doc.doctype = doc.deleted_doctype
		doc.docname = doc.deleted_name
		doc.deleted = 1

	return doc
