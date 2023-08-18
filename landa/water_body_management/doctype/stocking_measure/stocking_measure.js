// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

{% include "landa/water_body_management/stocking_controller.js" %}

frappe.ui.form.on("Stocking Measure", {
	onload: function(frm) {
		landa.utils.set_default_year(frm);
	}
});

cur_frm.script_manager.make(landa.StockingController);
