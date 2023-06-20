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
			frm.set_value("year", moment().year() - 1);
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
		var today = new Date();
        var current_year = today.getFullYear();
        var current_month = today.getMonth() + 1;
        var default_year;

        if (current_month < 7) {
            default_year = current_year - 1;
        } else {
            default_year = current_year;
        }

        if (!frm.doc.year_field) {
            frm.set_value("year", default_year);
        }
	},
});
