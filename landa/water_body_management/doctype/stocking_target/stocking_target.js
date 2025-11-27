// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
frappe.provide("landa.water_body_management");
landa.water_body_management.StockingTarget = class StockingTarget extends (
	landa.water_body_management.StockingController
) {
	refresh() {
		if (super.refresh) super.refresh();

		this.frm.add_custom_button(__("Create Stocking Measure"), () =>
			frappe.model.open_mapped_doc({
				method: "landa.water_body_management.doctype.stocking_target.stocking_target.create_stocking_measure",
				frm: this.frm,
			})
		);
	}
};

cur_frm.script_manager.make(landa.water_body_management.StockingTarget);
