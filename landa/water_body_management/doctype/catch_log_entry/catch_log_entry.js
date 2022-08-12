// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Catch Log Entry", {
	onload: function (frm) {
		if (frm.is_new() && !frm.doc.year) {
			frm.set_value("year", moment().year() - 1);
		}
	},
});
