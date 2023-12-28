import json

import firebase_admin
import frappe
from firebase_admin import credentials, messaging
from frappe import _

from landa.water_body_management.change_log import ChangeLog


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
	"""Enqueue this on hooks.py to send firebase notification on document creation"""
	enabled, file_path = frappe.get_value(
		"Water Body Management Settings", None, ["enable_firebase_notifications", "api_file_path"]
	)
	if not enabled:
		return

	# doc must have keys same as `ChangeLog()._get_changed_data` query
	change_log = ChangeLog().format_change(doc)

	cred = credentials.Certificate(file_path)
	firebase_admin.initialize_app(cred)

	# `create_firebase_notification` must be triggered on
	# Version Doc creation:
	# 	for: "Water Body", "Fish Species", "File","Water Body Management Local Organization", "Water Body Rules",
	# 	File if: file's ref docs is Water Body
	# Deleted Document Doc creation:
	# 	for: "Water Body", "Fish Species", "File","Water Body Management Local Organization"
	# Format and send notification
	message = messaging.Message(
		notification=messaging.Notification(
			title="Water Body" + "Created/Updated/Deleted",
			body=json.dumps(change_log),
		),
		token="<TOKEN>",
	)

	# Send a message to the device corresponding to the provided
	# registration token.
	response = messaging.send(message)
	# Response is a message ID string.
	print("Successfully sent message:", response)
