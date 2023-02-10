// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order",  {
    setup: function (frm) {
		frm.set_query("shipping_contact", erpnext.queries.contact_query);
	},
    refresh: function (frm) {
        frm.set_query("item_code", "items", function(doc) {
            return {
                query: "erpnext.controllers.queries.item_query",
                filters: {
                    valid_from_year: ["<=", doc.year_of_settlement],
                    valid_to_year: [">=", doc.year_of_settlement],
                    cannot_be_ordered: 0,
                    is_sales_item: 1
                }
            };
        });

        frm.set_query("selling_price_list", function(doc) {
            return {
                filters: {
                    selling: 1,
                    company: doc.company,
                }
            };
        });
    },
    before_save: function (frm) {
        frm.doc.items = landa.selling.remove_zero_qty_items(frm.doc.items);
    },
    year_of_settlement: function (frm) {
        landa.selling.prefill_items(frm);
        frm.doc.delivery_date = new Date(frm.doc.year_of_settlement, 11, 31); // the month is 0-indexed
    },
    shipping_contact: function (frm) {
        landa.selling.set_contact_details(frm, "shipping");
    }
});
