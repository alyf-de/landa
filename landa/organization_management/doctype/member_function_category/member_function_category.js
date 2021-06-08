// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Member Function Category', {
	refresh: function(frm) {
		if (has_common(frappe.user_roles, ["Administrator", "System Manager"])) {
			if (!frm.roles_editor) {
				const role_area = $(frm.fields_dict.roles_html.wrapper);
				frm.roles_editor = new frappe.RoleEditor(role_area, frm);
			}
			frm.roles_editor.show();
		}
	},

	validate: function(frm) {
		if (frm.roles_editor) {
			frm.roles_editor.set_roles_in_table();
		}
	}
});
