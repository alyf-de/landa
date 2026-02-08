// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stocking Plan Import", {
	onload(frm) {
		frm.set_query("organization", function () {
			return {
				filters: {
					parent_organization: frappe.boot.landa.state_organization,
					name: frappe.boot.landa.regional_organization,
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

		if (!frm.doc.organization && frappe.boot.landa.regional_organization) {
			frm.set_value("organization", frappe.boot.landa.regional_organization);
		}
	},

	after_save(frm) {
		frm.clear_table("items");
		frm.refresh_field("items");
	},
});
