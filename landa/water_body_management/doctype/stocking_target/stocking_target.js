// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

{% include "landa/water_body_management/stocking_controller.js" %}


frappe.ui.form.on("Stocking Target", {
	onload: function (frm) {
		landa.utils.set_default_year(frm);
	},
	refresh: function (frm) {
		frm.add_custom_button(__("Create Stocking Measure"), () =>
			frappe.model.open_mapped_doc({
				method:
					"landa.water_body_management.doctype.stocking_target.stocking_target.create_stocking_measure",
				frm: frm,
			})
		);
	},
	onload: function (frm) {
		const today = new Date();
		const current_year = today.getFullYear();

		let target_year;
		if (today.getMonth() < 10) {
			target_year = current_year;
		}
		else {
			target_year = current_year + 1;
		}
		frm.set_value('year', target_year);
	}
	});

cur_frm.script_manager.make(landa.StockingController);
