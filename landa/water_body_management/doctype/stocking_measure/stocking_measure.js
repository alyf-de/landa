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
				query: "landa.water_body_management.doctype.stocking_measure.stocking_measure.stocking_site_query",
				filters: {
					water_body: doc.water_body,
					fish_species: doc.fish_species,
					fish_type_for_stocking: doc.fish_type_for_stocking,
				},
			};
		});
	},
});