// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order",  {
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
            }
        });
    },
    before_save: function (frm) {
        frm.doc.items = frm.doc.items.filter(function (value) {
            return value.qty != 0;
        });
    },
    year_of_settlement: function (frm) {
        landa.prefill_items(frm);
        frm.doc.delivery_date = new Date(frm.doc.year_of_settlement, 11, 31); // the month is 0-indexed
    },
});

frappe.ui.form.on("Sales Order Item", {
    price_list_rate: function (frm, cdt, cdn) {
        // `price_list_rate` is set only once, when item details are loaded. We
        // use this as an indicator to see that all item details are complete.
        // Then we reset the quantity from 1 to 0.
        frappe.model.set_value(cdt, cdn, "qty", 0);
    }
});