// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Catch Log Entry", {
	onload: (frm) => {
		if (frm.is_new() && !frm.doc.year) {
			frm.set_value("year", moment().year() - 1);
		}
	},
	refresh: (frm) => {
		if (frm.doc.docstatus < 1 && frm.doc.__unsaved)	{
			// to avoid primary action refresh on dirty form (setting field value)
			frm.disable_save();

			frm.page.set_primary_action(__("Save and New"), () => {
				frappe.run_serially([
					() => frm.save(),
					() => frm.reload_doc(),
					() => frappe.new_doc("Catch Log Entry", {
						organization: frm.doc.organization
					}),
				]);
			});

			frm.page.set_secondary_action(__("Save"), () => {
				frm.save();
	   		});
	   }
   },
});
