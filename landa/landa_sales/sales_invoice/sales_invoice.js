frappe.ui.form.on("Sales Invoice", {
	setup: function (frm) {
		frm.set_query("shipping_contact", erpnext.queries.contact_query);
	},
	shipping_contact: function (frm) {
		landa.selling.set_contact_details(frm, "shipping");
	},
});
