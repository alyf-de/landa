// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Assignment", {
	setup(frm) {
		frm.set_query("organization", function () {
			return {
				filters: {
					is_group: 0,
				},
			};
		});

		frm.set_query("member", "members", function (doc) {
			return {
				filters: {
					organization: ["=", doc.organization],
				},
			};
		});
	},
});
