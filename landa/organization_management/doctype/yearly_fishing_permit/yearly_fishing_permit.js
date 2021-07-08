// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Yearly Fishing Permit', {
	setup: function(frm) {
		frm.set_query('type', function() {
			return {
				filters: {
					'docstatus': ["!=","0"]
				}
			}
		})
	}
});
