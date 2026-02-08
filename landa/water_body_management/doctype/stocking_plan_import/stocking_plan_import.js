// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stocking Plan Import", {
	setup(frm) {
		// prevent creation of footer with comment box and timeline
		frm.meta.hide_toolbar = true;
	},

	refresh(frm) {
		// hide sidebar
		frm.sidebar.sidebar.toggle(false);
		frm.page.sidebar.addClass("hide-sidebar");
	},

	onload(frm) {
		if (frm.is_new()) {
			frappe.set_route("Form", frm.doc.doctype, __("New Stocking Plan Import"));
		}

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
