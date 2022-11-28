frappe.ui.form.on("User", {
	refresh(frm) {
		if (
			!frm.is_new()
			&& frappe.perm.has_perm("User", 0, "write")
			&& frm.doc.name !== frappe.session.user
		) {
			frm.set_df_property("enabled", "read_only", 0);
		}
	},
});
