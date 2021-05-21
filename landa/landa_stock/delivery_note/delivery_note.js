frappe.ui.form.on('Delivery Note',  {
    refresh: function (frm) {
        frm.trigger('set_item_query')
    },
    year_of_settlement: function (frm) {
        frm.trigger('set_item_query')
    },
    set_item_query: function(frm) {
        const filters = {
            'valid_from_year': ["<=", frm.doc.year_of_settlement],
            'valid_to_year': [">=", frm.doc.year_of_settlement],
            'cannot_be_ordered': 0,
            'is_sales_item': 1
        }

        if (frm.doc.is_return) {
            // some items cannot be returned
            filters['cannot_be_returned'] = 0
        }

        frm.set_query("item_code", "items", function () {
            return {
                query: "erpnext.controllers.queries.item_query",
                filters: filters
            };
        });
        frm.clear_table("items");
        frm.refresh_field("items");
    }
});