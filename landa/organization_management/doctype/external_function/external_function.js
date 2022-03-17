// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("External Function", {
	onload: function (frm) {
		frm.set_query("organization", () => {
			return {
				filters: {
					parent_organization: "LV",
				},
			};
		});
	},
});
