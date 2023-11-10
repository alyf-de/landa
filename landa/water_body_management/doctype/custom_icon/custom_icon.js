// Copyright (c) 2023, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Custom Icon", {
	refresh: function (frm) {
		if (!frm.is_new() && !frm.doc.icon) {
			frm.dashboard.set_headline(__("Please attach an icon file."));
		}
	},
});
