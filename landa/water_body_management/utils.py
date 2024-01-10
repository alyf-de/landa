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
	if not doc_eligible(doc):
		return

	enabled, file_path, topic, project_id = get_firebase_settings()
	if not enabled:
		return

	# doc must have keys same as `ChangeLog()._get_changed_data` query
	formatted_doc = format_doc_for_change_log(doc)
	change_log = ChangeLog().format_change(formatted_doc)
	if not change_log:
		return

	# Send notification to topic
	frappe.enqueue(
		send_firebase_notification,
		queue="default",
		file_path=file_path,
		project_id=project_id,
		topic=topic,
		change_log=change_log,
	)


def send_firebase_notification(file_path, project_id, topic, change_log):
	try:
		fcm = FirebaseNotification(file_path, project_id)
		response = fcm.send_to_topic(topic, change_log)
		response.raise_for_status()
	except Exception:
		frappe.log_error(message=frappe.get_traceback(), title=_("Firebase Notification Error"))


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


def get_firebase_settings():
	"""Get Firebase Settings"""
	return frappe.get_cached_value(
		"Water Body Management Settings",
		None,
		["enable_firebase_notifications", "api_file_path", "firebase_topic", "project_id"],
	)
