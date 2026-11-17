// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
	setup: function (frm) {
		frm.set_query("shipping_contact", erpnext.queries.contact_query);
		frm.trigger("set_item_query");
	},
	refresh: function (frm) {
		frm.trigger("set_item_query");

		if (frm.is_new()) {
			landa.utils.set_company_and_customer(frm);
			landa.utils.set_default_year(frm, "year_of_settlement");
			frm.trigger("prefill_items_if_empty");
		}

		frm.set_query("selling_price_list", function (doc) {
			return {
				filters: {
					selling: 1,
					company: doc.company,
				},
			};
		});

		if (!frappe.user.has_role("LANDA Regional Organization Management")) {
			setTimeout(function () {
				frm.remove_custom_button(__("Hold"), __("Status"));
				frm.remove_custom_button(__("Close"), __("Status"));
				frm.remove_custom_button(__("Re-open"), __("Status"));
				frm.remove_custom_button(__("Update Items"));
			}, 500);
		}

		setTimeout(function () {
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
	set_item_query: function (frm) {
		// CAUTION: needs to run before triggering year_of_settlement!
		frm.set_query("item_code", "items", function (doc) {
			return {
				query: "erpnext.controllers.queries.item_query",
				filters: {
					valid_from_year: ["<=", doc.year_of_settlement],
					valid_to_year: [">=", doc.year_of_settlement],
					cannot_be_ordered: 0,
					is_sales_item: 1,
					company: doc.company,
				},
			};
		});
	},
	before_save: function (frm) {
		frm.doc.items = landa.selling.remove_zero_qty_items(frm.doc.items);
	},
	customer: function (frm) {
		frm.trigger("prefill_items_if_empty");
	},
	company: function (frm) {
		frm.trigger("prefill_items_if_empty");
	},
	year_of_settlement: function (frm) {
		// A date string, not a `Date`: a `Date` is sent as a UTC timestamp, which the
		// database rejects or which is the day before in a time zone east of UTC.
		const year = frm.doc.year_of_settlement;
		frm.doc.delivery_date = year ? `${year}-12-31` : null;
		frm.trigger("prefill_items");
	},
	prefill_items_if_empty: function (frm) {
		const has_items = frm.doc.items.some((row) => row.item_code);
		if (!has_items) {
			frm.trigger("prefill_items");
		}
	},
	prefill_items: function (frm) {
		const { name, customer, company, year_of_settlement } = frm.doc;
		const is_complete = customer && company && year_of_settlement;
		const prefill_key = is_complete ? [name, company, year_of_settlement].join("|") : "";

		// Several fields can trigger this for the same document, company and year
		// (e.g. the defaults set on refresh). Fill the table only once per combination.
		if (is_complete && frm.landa_prefill_key === prefill_key) {
			return;
		}

		frm.landa_prefill_key = prefill_key;
		const request = landa.selling.prefill_items(frm); // clears the table if a prerequisite is missing

		// A failed request leaves the table unfilled. Let the next trigger try again.
		request?.catch(() => {
			if (frm.landa_prefill_key === prefill_key) {
				frm.landa_prefill_key = "";
			}
		});
	},
	shipping_contact: function (frm) {
		landa.selling.set_contact_details(frm, "shipping");
	},
});
