// Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order',  {
    refresh: function (frm) {
        frm.set_query("item_code", "items", function() {
            return {
                query: "erpnext.controllers.queries.item_query",
                filters: {
                    'valid_from_year': ["<=", frm.doc.year_of_settlement],
                    'valid_to_year': [">=", frm.doc.year_of_settlement],
                    'cannot_be_ordered': 0,
                    'is_sales_item': 1
                }
            }
        });
    },
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
        frappe.call({
            method: "landa.organization_management.doctype.member.member.belongs_to_parent_organization",
            callback: function(r) {
                if (!r.message) {
                    if (frm.doc.customer != null && frm.doc.year_of_settlement != null) {
                        frappe.call({
                            method: "landa.landa_sales.sales_order.sales_order.get_items",
                            args: {
                                'year': frm.doc.year_of_settlement
                            },
                            callback: function (r) {
                                frm.clear_table("items");
                                frm.refresh_field("items");
                                for (const item of r.message) {
                                    const row = frm.add_child("items");
                                    Object.assign(row, item);
                                }
                                frm.refresh_field("items");
                            }
                        })
                    }
                    else {
                        frm.clear_table("items");
                        frm.refresh_field("items");
                    }
                } else {
                    frm.clear_table("items");
                    frm.refresh_field("items");
                }
            }
        });
    }
});
