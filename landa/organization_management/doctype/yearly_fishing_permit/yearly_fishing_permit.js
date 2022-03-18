// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Yearly Fishing Permit", {
	onload: function (frm) {
		frm.set_query("type", function () {
			return {
				filters: {
					docstatus: ["!=", "0"],
				},
			};
		});
		if (frm.is_new() && !frm.doc.year) {
			frm.trigger("set_default_year");
		}
	},
	set_default_year: function (frm) {
		// set default year to the current year if it's before november,
		// else to the next year
		const now = moment();
		let year = now.year();
		if (now.month() >= 11) {
			year += 1;
		}
		frm.set_value("year", year);
	},
});
