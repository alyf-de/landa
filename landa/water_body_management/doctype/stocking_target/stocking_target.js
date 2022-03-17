// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stocking Target", {
	refresh: function (frm) {
		frm.trigger("weight");
		frm.trigger("quantity");
	},
	weight: function (frm) {
		if (!frm.doc.weight || !frm.doc.water_body_size) {
			frm.set_value("weight_per_water_body_size", 0.0);
		} else {
			frm.set_value(
				"weight_per_water_body_size",
				flt(frm.doc.weight / frm.doc.water_body_size, 3)
			);
			frm.set_value(
				"unit_of_weight_per_water_body_size",
				`Kg / ${frm.doc.water_body_size_unit}`
			);
		}

		frm.trigger("update_price");
	},
	quantity: function (frm) {
		if (!frm.doc.quantity || !frm.doc.water_body_size) {
			frm.set_value("quantity_per_water_body_size", 0);
		} else {
			frm.set_value(
				"quantity_per_water_body_size",
				flt(frm.doc.quantity / frm.doc.water_body_size, 3)
			);
			frm.set_value(
				"unit_of_quantity_per_water_body_size",
				`Stk / ${frm.doc.water_body_size_unit}`
			);
		}
	},
	price_per_kilogram: function (frm) {
		frm.trigger("update_price");
	},
	update_price: function (frm) {
		if (!frm.doc.weight || !frm.doc.price_per_kilogram) {
			frm.set_value("price_for_total_weight", 0);
		} else {
			frm.set_value(
				"price_for_total_weight",
				flt(frm.doc.weight * frm.doc.price_per_kilogram, 2)
			);
		}
	},
});
