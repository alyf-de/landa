frappe.ui.form.on("Sales Invoice", {
	setup: function (frm) {
		frm.set_query("shipping_contact", erpnext.queries.contact_query);
	},
	shipping_contact: function (frm) {
		landa.selling.set_contact_details(frm, "shipping");
	},
	refresh: function (frm) {
		if (frm.is_new()) {
			landa.utils.set_company_and_customer(frm);
		}
	},
});
