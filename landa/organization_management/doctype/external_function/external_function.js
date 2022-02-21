// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('External Function', {
	refresh: function(frm) {
		frm.trigger('set_external_function_category_query');
	},
	set_external_function_category_query: function(frm) {
		if (frappe.user.has_role('LANDA State Organization Employee')) {
			return;
		} else if (frappe.user.has_role('LANDA Regional Organization Management')) {
			frm.set_query('external_function_category', () => {
				return {
					filters: {
						access_level: ['in', ['Regional Organization', 'Local Organization']]
					}
				};
			});
		} else if (frappe.user.has_role('LANDA Local Organization Management')) {
			frm.set_query('external_function_category', () => {
				return {
					filters: {
						access_level: 'Local Organization'
					}
				};
			});
		}
	}
});

