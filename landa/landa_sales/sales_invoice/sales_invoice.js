frappe.ui.form.on("Sales Invoice", {
	setup: function (frm) {
		frm.set_query("shipping_contact", erpnext.queries.contact_query);
		frm.trigger("set_item_query");
	},
	shipping_contact: function (frm) {
		landa.selling.set_contact_details(frm, "shipping");
	},
	refresh: function (frm) {
		if (frm.is_new()) {
			landa.utils.set_company_and_customer(frm);
		}

		setTimeout(() => {
			frm.remove_custom_button(__("Fetch Timesheet"));
			frm.remove_custom_button(__("Quotation"), __("Get Items From"));
		}, 500);

		frm.trigger("set_item_query");
	},
	set_item_query: function (frm) {
		frm.set_query("item_code", "items", function (doc) {
			return {
				query: "erpnext.controllers.queries.item_query",
				filters: {
					valid_from_year: ["<=", doc.year_of_settlement],
					valid_to_year: [">=", doc.year_of_settlement],
					is_sales_item: 1,
					company: doc.company,
				},
			};
		});
	},
});
