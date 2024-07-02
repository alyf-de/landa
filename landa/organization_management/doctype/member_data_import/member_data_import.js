// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member Data Import", {
	after_save: function (frm) {
		frappe.show_alert({
			message: __("LANDA Member {0} has been created or updated.", [
				frappe.utils.get_form_link("LANDA Member", frm.doc.member, true),
			]),
			indicator: "green",
		});
		frappe.new_doc("Member Data Import");
	},
});
