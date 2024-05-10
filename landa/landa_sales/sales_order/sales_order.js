// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order",  {
    setup: function (frm) {
        frm.set_query("shipping_contact", erpnext.queries.contact_query);
    },
    refresh: function (frm) {
        if (frm.is_new()) {
            landa.utils.set_company_and_customer(frm);
        }

        frm.set_query("item_code", "items", function(doc) {
            return {
                query: "erpnext.controllers.queries.item_query",
                filters: {
                    valid_from_year: ["<=", doc.year_of_settlement],
                    valid_to_year: [">=", doc.year_of_settlement],
                    cannot_be_ordered: 0,
                    is_sales_item: 1,
                    company: doc.company,
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

        if (!frappe.user.has_role("LANDA Regional Organization Management")) {
            setTimeout(function() {
                frm.remove_custom_button(__("Hold"), __("Status"));
                frm.remove_custom_button(__("Close"), __("Status"));
            }, 500);
        }

        setTimeout(function() {
            frm.remove_custom_button(__("Pick List"), __("Create"));
            frm.remove_custom_button(__("Work Order"), __("Create"));
            frm.remove_custom_button(__("Material Request"), __("Create"));
            frm.remove_custom_button(__("Request for Raw Materials"), __("Create"));
            frm.remove_custom_button(__("Purchase Order"), __("Create"));
            frm.remove_custom_button(__("Project"), __("Create"));
            frm.remove_custom_button(__("Subscription"), __("Create"));
            frm.remove_custom_button(__("Payment Request"), __("Create"));
            frm.remove_custom_button(__("Payment Request"), __("Create"));
        }, 500);
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
