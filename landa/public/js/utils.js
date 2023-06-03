frappe.provide("landa");

landa.utils = {
	setup_regional_organization_filter: function (listview, filter_name) {
		if (Object.hasOwn(listview.page.fields_dict, filter_name)) {
			listview.page.fields_dict[filter_name].get_query =
				landa.queries.regional_organization_query;
		}
	},
	set_default_year: function set_default_year(frm) {
    // set default year to the current year if it's before november,
    // else to the next year
    const now = moment();
    let year = now.year();
    if (now.month() >= 11) {
        year += 1;
    }
    frm.set_value("year", year);
}
};
