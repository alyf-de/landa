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
	refresh: function (frm) {
		frm.trigger("render_default_addresses");
		frm.trigger("render_member_functions");
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
								(addr) => addr.name == frm.doc[address],
							),
						}),
					)
					.find(".btn-address")
					.remove();
			} else {
				$(frm.fields_dict[address + "_html"].wrapper).empty();
			}
		});
	},
	render_member_functions: function (frm) {
		const member_functions = (frm.doc.__onload || {}).active_member_functions || [];
		frm.fields_dict.custom_active_member_functions.wrapper.innerHTML =
			landa.utils.render_static_grid({
				id: "customer_member_functions_grid",
				label: __("Member Functions"),
				data: member_functions,
				columns: get_customer_member_function_columns(),
			});
	},
});

function get_customer_member_function_columns() {
	return [
		{
			fieldname: "member_function_category",
			label: __("Function"),
			fieldtype: "Link",
			width: 4,
			route: (row) => ["member-function", row.name],
		},
		{
			fieldname: "member",
			label: __("Member"),
			fieldtype: "Link",
			width: 5,
			value: (row) =>
				[row.member_first_name, row.member_last_name].filter(Boolean).join(" ") ||
				row.member,
			route: (row) => ["landa-member", row.member],
		},
		{
			fieldname: "start_date",
			label: __("Since"),
			fieldtype: "Date",
			width: 3,
			formatter: (value) => (value ? frappe.datetime.str_to_user(value) : ""),
		},
	];
}
