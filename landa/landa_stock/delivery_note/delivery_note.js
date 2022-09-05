frappe.ui.form.on("Delivery Note",  {
    refresh: function (frm) {
        frm.trigger("set_item_query");
    },
    set_item_query: function(frm) {
        frm.set_query("item_code", "items", function () {
            const filters = {
                valid_from_year: ["<=", frm.doc.year_of_settlement],
                valid_to_year: [">=", frm.doc.year_of_settlement],
                is_sales_item: 1
            }

            if (frm.doc.is_return) {
                // some items cannot be returned
                filters["cannot_be_returned"] = 0;
            }

            return {
                query: "erpnext.controllers.queries.item_query",
                filters: filters
            };
        });
    },
    year_of_settlement: function (frm) {
        // don't prefill items if the table is already populated
        if (frm.doc.items.length >= 1 && frm.doc.items[0].item_code) return;
        landa.selling.prefill_items(frm);
    },
    before_save: function (frm) {
        frm.doc.items = landa.selling.remove_zero_qty_items(frm.doc.items);
    },
});
