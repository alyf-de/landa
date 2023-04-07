// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Water Body", {
	refresh: function (frm) {
		if (
			!frm.is_new() &&
			frappe.boot.landa.regional_organization &&
			frm.doc.organization !== frappe.boot.landa.regional_organization
		) {
			frm.disable_form();
		}
	},
});
