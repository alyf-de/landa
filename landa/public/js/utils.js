frappe.provide("landa");

landa.utils = {
	setup_regional_organization_filter: function (listview, filter_name) {
		if (Object.hasOwn(listview.page.fields_dict, filter_name)) {
			listview.page.fields_dict[filter_name].get_query =
				landa.queries.regional_organization_query;
		}
	},
};
