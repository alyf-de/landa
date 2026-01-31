// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Ledger Entry", {
	setup(frm) {
		frm.set_query("member", function () {
			return {
				filters: { organization: frm.doc.organization },
			};
		});
	},
});
