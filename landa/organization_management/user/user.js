frappe.ui.form.on("User", {
	refresh(frm) {
		if (
			!frm.is_new()
			&& frappe.perm.has_perm("User", 0, "write")
			&& frm.doc.name !== frappe.session.user
		) {
			frm.set_df_property("enabled", "read_only", 0);
		} else {
			frm.set_df_property("enabled", "read_only", 1);
		}

		// set link to LANDA Member only once
		if (frm.doc.landa_member) {
			frm.set_df_property("landa_member", "read_only", 1);
		} else {
			frm.set_df_property("landa_member", "read_only", 0);
		}
	},
});
