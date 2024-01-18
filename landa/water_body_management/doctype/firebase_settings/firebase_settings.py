# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt
import json
from io import BytesIO
from pathlib import Path

import frappe
from frappe import _
from frappe.model.document import Document


class FirebaseSettings(Document):
	def validate(self):
		if self.enable_firebase_notifications and not self.project_id:
			frappe.throw(
				msg=_("Please upload the Firebase API file."),
				title=_("Missing Project ID"),
			)

		if self.enable_firebase_notifications and not self.has_credentials:
			frappe.throw(
				msg=_("Please upload the Credentials file."),
				title=_("Missing Credentials"),
			)

	@property
	def credentials_path(self):
		return get_crendentials_path()

	@property
	def has_credentials(self):
		return self.credentials_path.exists()

	@frappe.whitelist()
	def needs_credentials(self):
		return not self.has_credentials


@frappe.whitelist()
def upload_api_file(*args, **kwargs):
	frappe.has_permission("Firebase Settings", "write", throw=True)

	json_data = json.load(BytesIO(frappe.local.uploaded_file))
	project_id = json_data.get("project_id")
	if not project_id:
		frappe.throw(
			msg=_("The uploaded file does not contain a project id."),
			title=_("Missing Project ID"),
		)

	credentials_path = get_crendentials_path()
	credentials_path.parent.mkdir(exist_ok=True)
	credentials_path.write_text(json.dumps(json_data, indent=1))

	return {"doctype": "File", "data": {"project_id": project_id}}


def get_crendentials_path():
	return Path(frappe.local.site_path) / "firebase" / "credentials.json"
