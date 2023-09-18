frappe.provide("landa");

landa.utils = {
	setup_regional_organization_filter: function (listview, filter_name) {
		if (Object.hasOwn(listview.page.fields_dict, filter_name)) {
			listview.page.fields_dict[filter_name].get_query =
				landa.queries.regional_organization_query;
		}
	},
	/* Write the default year into the form's [fieldname] field
	 * if the form is new and the field is empty.

	 * @param {Object} frm - The form object
	 * @param {String} fieldname - The name of the field to set
	*/
	set_default_year: function (frm, fieldname = "year") {
		if (frm.is_new() && !frm.doc[fieldname]) {
			frm.set_value(fieldname, landa.utils.get_default_year());
		}
	},
	/* Return the current year if it's before november, else the next year */
	get_default_year: function () {
		const today = new Date();
		const current_year = today.getFullYear();
		const current_month = today.getMonth();

		return current_month < 10 ? current_year : current_year + 1;
	},
};
