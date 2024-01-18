# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt
import json
import os

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.file_manager import get_file


class FirebaseSettings(Document):
	def validate(self):
		if self.enable_firebase_notifications and not self.project_id:
			frappe.throw(
				msg=_("Please upload the Firebase API file."),
				title=_("Missing Project ID"),
			)


@frappe.whitelist()
def upload_api_file(file_url: str, file_id: str):
	frappe.only_for("System Manager")

	file_data = json.loads(get_file(file_url)[1])
	project_id = file_data.get("project_id")
	if not project_id:
		frappe.throw(
			msg=_("The uploaded file does not contain a project id."),
			title=_("Missing Project ID"),
		)

	# Write file contents to sites/sitename/firebase/firebase-credentials.json
	folder_path = f"{frappe.local.site_path}/firebase"
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)

	with open(f"{folder_path}/credentials.json", "w") as f:
		json.dump(file_data, f, indent=1)

	# Delete file, it was used temporarily. Hard to overwrite File uploader file creation action
	frappe.delete_doc("File", file_id)

	# Return project id for settings
	return {"project_id": project_id}
