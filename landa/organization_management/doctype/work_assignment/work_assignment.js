// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Assignment", {
	setup(frm) {
		const can_select_any =
			frappe.user.has_role("LANDA State Organization Employee") ||
			frappe.user.has_role("LANDA Regional Organization Management");
		const local_organization = frappe.boot.landa?.local_organization;

		if (!can_select_any && local_organization && frm.is_new()) {
			frm.set_value("organization", local_organization);
		}

		frm.set_query("organization", function () {
			let filters = { is_group: 0 };
			if (!can_select_any && local_organization) {
				filters.name = local_organization;
			}
			return { filters };
		});

		frm.set_query("member", "members", function (doc) {
			return {
				filters: {
					organization: doc.organization,
				},
			};
		});
	},
});

frappe.ui.form.on("Work Assignment Member", {
	member(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		if (!row.duration && frm.doc.planned_duration) {
			frappe.model.set_value(cdt, cdn, "duration", frm.doc.planned_duration);
		}
	},
});
