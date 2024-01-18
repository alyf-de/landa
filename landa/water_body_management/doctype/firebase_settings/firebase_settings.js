// Copyright (c) 2024, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Firebase Settings", {
	refresh: (frm) => {
		frm.call("needs_credentials").then(({ message }) => {
			if (message) {
				frm.events.add_upload_credentials_button(frm);
			}
		});
	},

	add_upload_credentials_button: (frm) => {
		frm.add_custom_button(__("Upload Firebase Credentials"), function () {
			new frappe.ui.FileUploader({
				method: "landa.water_body_management.doctype.firebase_settings.firebase_settings.upload_api_file",
				allow_multiple: false,
				restrictions: {
					allowed_file_types: [".json"],
				},
				on_success: function ({ data }) {
					frappe.show_alert({
						message: __("Firebase credentials uploaded successfully"),
						indicator: "green",
					});
					frm.set_value("project_id", data.project_id);
					if (frm.is_dirty()) {
						// project id might be unchanged
						frm.save();
					} else {
						frm.refresh();
					}
				},
			});
		});
	},
});
