// Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order',  {
    before_save: function (frm) {
        frm.doc.items = frm.doc.items.filter(function (value) {
            return value.qty != 0;
        });
    },
    customer: function (frm) {
        frm.trigger('prefill_items');
    },
    year_of_settlement: function (frm) {
        frm.trigger('prefill_items');
    },
    prefill_items: function (frm) {
        if (frm.doc.customer != null && frm.doc.year_of_settlement != null) {
            frappe.call({
                method: "landa.landa_sales.sales_order.sales_order.get_items",
                args: {
                    'year': frm.doc.year_of_settlement
                },
                callback: function (r) {
                    frm.clear_table("items")
                    frm.refresh_field("items")
                    for (const item of r.message) {
                        const row = frm.add_child("items")
                        row.item_code = item.item_code
                        row.item_name = item.item_name
                        row.cannot_be_returned = item.cannot_be_returned
                        row.description = item.description
                        row.delivery_date = item.delivery_date
                        row.uom = item.uom
                        row.uom_factor = item.uom_factor
                        row.qty = item.qty
                        row.rate = item.rate
                    }
                    frm.refresh_field("items");
                }
            })
        }
        else {
            frm.clear_table("items")
            frm.refresh_field("items")
        }
    }
});