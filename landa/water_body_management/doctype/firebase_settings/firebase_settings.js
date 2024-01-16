// Copyright (c) 2024, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Firebase Settings", {
	refresh: (frm) => {
		if (frm.doc.enable_firebase_notifications) {
			frm.events.upload_api_file_button(frm);
		}
	},

	enable_firebase_notifications: (frm) => {
		if (frm.doc.enable_firebase_notifications) {
			frm.events.upload_api_file_button(frm);
		} else {
			frm.remove_custom_button(__("Upload Firebase API File"))
		}
	},

	upload_api_file_button: (frm) => {
		frm.add_custom_button(__("Upload Firebase API File"), function() {
			new frappe.ui.FileUploader({
				allow_multiple: false,
				restrictions: {
					allowed_file_types: [".json"]
				},
				on_success(file_doc) {
					frappe.call({
						method: "landa.water_body_management.doctype.firebase_settings.firebase_settings.upload_api_file",
						args: {
							file_url: file_doc.file_url,
							file_id: file_doc.name
						},
						freeze: true,
						freeze_message: __("Configuring Firebase API ..."),
						callback: function(r) {
							if (r.message && !r.exc) {
								frm.set_value("project_id", r.message.project_id);
								frm.save();
							}
						}
					});
				}
			});
		});
	}
});
