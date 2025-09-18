// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Landlord", {
	refresh: function (frm) {
		frm.set_query("regional_organization", landa.queries.regional_organization_query);
	},
});
