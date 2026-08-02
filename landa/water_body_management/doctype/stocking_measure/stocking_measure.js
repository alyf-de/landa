// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
frappe.provide("landa.water_body_management");
landa.water_body_management.StockingMeasure = class StockingMeasure extends (
	landa.water_body_management.StockingController
) {};

cur_frm.script_manager.make(landa.water_body_management.StockingMeasure);

frappe.ui.form.on("Stocking Measure", {
	setup(frm) {
		frm.set_query("stocking_site", (doc) => {
			return {
				filters: [["Stocking Site", "water_body", "=", doc.water_body]],
			};
		});
	},
});