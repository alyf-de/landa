frappe.ui.form.on('Delivery Note',  {
    refresh: function (frm) {
        if (frm.doc.is_return) {
            // some items cannot be returned
            frm.set_query("item_code", "items", function () {
                return {
                    query: "erpnext.controllers.queries.item_query",
                    filters: {
                        'cannot_be_returned': 0,
                        'is_sales_item': 1
                    }
                };
            });
        }
    },
    before_save: function (frm) {
        frm.doc.items = frm.doc.items.filter(function (value) {
            return value.qty != 0;
        });
    },
    customer: function (frm) {
        frm.trigger('prefill_delivery_items');
    },
    year_of_settlement: function (frm) {
        frm.trigger('prefill_delivery_items');
    },
    prefill_delivery_items: function (frm) {
        if (frm.doc.customer != null && frm.doc.year_of_settlement != null) {
            frappe.call({
                method: "landa.landa_sales.delivery_note.delivery_note.get_items",
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