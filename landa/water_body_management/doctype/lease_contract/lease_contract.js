// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lease Contract', {
	onload: function (frm) {
		frm.set_query("organization", function (doc) {
			return {
				filters: {
					parent_organization: "LV",
				},
			};
		});

		frm.set_query("water_body", function (doc) {
			return {
				filters: {
					organization: doc.organization,
				},
			};
		});
	},
});
