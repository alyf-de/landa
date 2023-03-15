frappe.ui.form.on("Address", {
	setup(frm) {
		set_address_and_contact_queries(frm);
	},
});

frappe.ui.form.on("Contact", {
	setup(frm) {
		set_address_and_contact_queries(frm);
	},
});

function set_address_and_contact_queries(frm) {
	frm.set_query("landa_member", landa.queries.filter_by_organization);
	frm.set_query("customer", landa.queries.filter_by_organization);
	frm.set_query("external_contact", landa.queries.filter_by_organization);
}
