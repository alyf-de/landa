// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Water Body Management Local Organization", {
	onload: function (frm) {
		frm.set_query("organization", function (doc) {
			return {
				filters: {
					name: ["like", `${doc.regional_organization}-%`],
				},
			};
		});
		frm.set_query("landa_member", "water_body_local_contact_table", function (doc) {
			return {
				filters: {
					organization: doc.organization,
				},
			};
		});
	},
});
