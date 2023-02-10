frappe.ui.form.on("Customer", {
	setup: function (frm) {
		frm.set_query("default_billing_contact", erpnext.queries.contact_query);
		frm.set_query("default_shipping_contact", erpnext.queries.contact_query);
		frm.set_query("default_billing_address", function (doc) {
			return {
				filters: {
					link_doctype: "Customer",
					link_name: doc.name,
				},
			};
		});
		frm.set_query("default_shipping_address", function (doc) {
			return {
				filters: {
					link_doctype: "Customer",
					link_name: doc.name,
				},
			};
		});
	},
    refresh: function(frm) {
        frm.trigger("render_default_addresses");
    },
	default_billing_address: function (frm) {
		frm.trigger("render_default_addresses");
	},
	default_shipping_address: function (frm) {
		frm.trigger("render_default_addresses");
	},
	render_default_addresses: function (frm) {
		["default_billing_address", "default_shipping_address"].forEach((address) => {
			if (frm.doc[address]) {
				$(frm.fields_dict[address + "_html"].wrapper)
					.html(
						frappe.render_template("address_list", {
							addr_list: frm.doc.__onload["addr_list"].filter(
								(addr) => addr.name == frm.doc[address]
							),
						})
					)
					.find(".btn-address")
					.remove();
			} else {
				$(frm.fields_dict[address + "_html"].wrapper).empty();
			}
		});
	},
});
