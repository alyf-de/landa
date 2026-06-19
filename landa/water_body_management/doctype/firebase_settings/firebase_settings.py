# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt
import json
from io import BytesIO

import frappe
from frappe import _
from frappe.model.document import Document


class FirebaseSettings(Document):
	def validate(self):
		if self.enable_firebase_notifications and not self.project_id:
			frappe.throw(
				msg=_("Please upload a Firebase credentials file."),
				title=_("Missing Project ID"),
			)

		if self.enable_firebase_notifications and not self.has_credentials:
			frappe.throw(
				msg=_("Please upload a Firebase credentials file."),
				title=_("Missing Credentials"),
			)

	@property
	def has_credentials(self):
		return bool(self.get_password("credentials", raise_exception=False))


@frappe.whitelist(methods=["POST"])
def upload_api_file(*args, **kwargs):
	doc = frappe.get_single("Firebase Settings")
	doc.check_permission("write")

	json_data = json.load(BytesIO(frappe.local.uploaded_file))
	project_id = json_data.get("project_id")
	if not project_id:
		frappe.throw(
			msg=_("The uploaded file does not contain a project id."),
			title=_("Missing Project ID"),
		)

	doc.project_id = project_id
	doc.credentials = json.dumps(json_data)
	doc.save()

	return {"doctype": "File", "data": {"project_id": project_id}}
