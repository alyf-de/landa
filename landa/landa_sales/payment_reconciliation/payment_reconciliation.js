frappe.ui.form.on("Payment Reconciliation", {
	refresh: function (frm) {
		if (!frm.doc.customer) {
			frm.set_value("party_type", "Customer");
		}
	},
});
