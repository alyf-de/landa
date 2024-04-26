frappe.ui.form.on("Data Import", {
	refresh: function (frm) {
		frm.trigger("toggle_import_type");
	},
	reference_doctype: function (frm) {
		frm.trigger("toggle_import_type");
	},
	toggle_import_type: function (frm) {
		if (frm.doc.reference_doctype === "Member Data Import") {
			frm.set_df_property("import_type", "read_only", 1);
			frm.set_value("import_type", "Insert New Records");
		} else if (frm.is_new()) {
			frm.set_df_property("import_type", "read_only", 0);
		}
	},
});
