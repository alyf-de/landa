frappe.provide("landa.StockingController");

landa.StockingController = frappe.ui.form.Controller.extend({
    onload() {
		this.frm.set_query("organization", function (doc) {
			return {
				filters: {
					parent_organization: "LV",
					name: frappe.boot.landa.regional_organization,
				},
			};
		});
		this.frm.set_query("water_body", function (doc) {
			return {
				filters: {
					organization: doc.organization,
				},
			};
		});

		if (!this.frm.doc.organization && frappe.boot.landa.regional_organization) {
			this.frm.set_value("organization", frappe.boot.landa.regional_organization);
		}
	},
	water_body() {
		this.weight();
		this.quantity();
	},
    weight() {
		if (!this.frm.doc.weight || !this.frm.doc.water_body_size) {
			this.frm.set_value("weight_per_water_body_size", 0.0);
		} else {
			this.frm.set_value(
				"weight_per_water_body_size",
				flt(this.frm.doc.weight / this.frm.doc.water_body_size, 3)
			);
			this.frm.set_value(
				"unit_of_weight_per_water_body_size",
				`Kg / ${this.frm.doc.water_body_size_unit}`
			);
		}

		this.update_price();
	},
	quantity() {
		if (!this.frm.doc.quantity || !this.frm.doc.water_body_size) {
			this.frm.set_value("quantity_per_water_body_size", 0);
		} else {
			this.frm.set_value(
				"quantity_per_water_body_size",
				flt(this.frm.doc.quantity / this.frm.doc.water_body_size, 3)
			);
			this.frm.set_value(
				"unit_of_quantity_per_water_body_size",
				`Stk / ${this.frm.doc.water_body_size_unit}`
			);
		}
	},
	price_per_kilogram() {
		this.update_price();
	},
	update_price() {
		if (!this.frm.doc.weight || !this.frm.doc.price_per_kilogram) {
			this.frm.set_value("price_for_total_weight", 0);
		} else {
			this.frm.set_value(
				"price_for_total_weight",
				flt(this.frm.doc.weight * this.frm.doc.price_per_kilogram, 2)
			);
		}
	},
});