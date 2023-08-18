frappe.provide("landa");

landa.utils = {
	setup_regional_organization_filter: function (listview, filter_name) {
		if (Object.hasOwn(listview.page.fields_dict, filter_name)) {
			listview.page.fields_dict[filter_name].get_query =
				landa.queries.regional_organization_query;
		}
	},
	set_default_year: function (frm, fieldname = "year") {
		// set default year to the current year if it's before november,
		// else to the next year
		if (frm.is_new() && !frm.doc[fieldname]) {
			const today = new Date();
			const current_year = today.getFullYear();
			const current_month = today.getMonth();

			frm.set_value(fieldname, current_month < 10 ? current_year : current_year + 1);
		}
	}
};
