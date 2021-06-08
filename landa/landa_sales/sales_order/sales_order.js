// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order',  {
    refresh: function (frm) {
        frm.set_query('item_code', 'items', function() {
            return {
                query: 'erpnext.controllers.queries.item_query',
                filters: {
                    valid_from_year: ['<=', frm.doc.year_of_settlement],
                    valid_to_year: ['>=', frm.doc.year_of_settlement],
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
        frm.trigger('prefill_items');
        // the month is 0-indexed
        frm.doc.delivery_date = new Date(frm.doc.year_of_settlement, 11, 31);
    },
    prefill_items: function (frm) {
        if (frm.doc.customer && frm.doc.year_of_settlement) {
            frappe.call({
                method: 'erpnext.controllers.queries.item_query', // Use item query to get all selectable items
                args: {
                    doctype: 'Item',
                    txt: '', // empty search text returns all items
                    searchfield: 'name',
                    start: 0,
                    page_len: 99, // limit pre-filled items to 100
                    filters: {
                        valid_from_year: ['<=', frm.doc.year_of_settlement],
                        valid_to_year: ['>=', frm.doc.year_of_settlement],
                        cannot_be_ordered: 0,
                        is_sales_item: 1
                    },
                    as_dict: true
                },
                callback: function (r) {
                    frm.clear_table('items');
                    frm.refresh_field('items');

                    for (const item of r.message) {
                        const row = frm.add_child('items');
                        frappe.model.set_value(row.doctype, row.name, 'item_code', item.name);

                        // `ControlLink.validate()` does not get triggered by `frappe.model.set_value`,
                        // therefore we have to set the "fetch from"-fields manually.
                        frappe.model.set_value(row.doctype, row.name, 'cannot_be_returned', item.cannot_be_returned);
                    }
                }
            });
        } else {
            frm.clear_table('items');
            frm.refresh_field('items');
        }
    }
});
