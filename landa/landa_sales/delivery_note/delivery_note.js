frappe.ui.form.on('Delivery Note',  {
    refresh: function (frm) {
        if (frm.doc.is_return) {
            // some items cannot be returned
            frm.set_query("item_code", "items", function () {
                return {
                    filters: {
                        'cannot_be_returned': 0,
                        'is_sales_item': 1
                    }
                };
            });
        }
    },
});
