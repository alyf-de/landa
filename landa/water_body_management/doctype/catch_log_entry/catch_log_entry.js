// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Catch Log Entry", {
	setup: (frm) => {
		frm.set_indicator_formatter("fish_species", (row) =>
			row.plausible === 1 ? "green" : "orange"
		);
	},
	onload: (frm) => {
		if (frm.is_new() && !frm.doc.year) {
			const today = new Date();
			const current_year = today.getFullYear();
			const current_month = today.getMonth();

			if (!frm.doc.year) {
				frm.set_value("year", current_month < 6 ? current_year - 1 : current_year);
			}
		}
	},
	refresh: (frm) => {
		if (frm.doc.docstatus == 0 && !frm.is_new()) {
			frm.add_custom_button(__("New Catch Log Entry"), () => {
				frappe.new_doc(frm.doctype, {
					organization: frm.doc.organization,
					year: frm.doc.year,
				});
			});
		}
	},
});
