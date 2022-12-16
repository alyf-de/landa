frappe.listview_settings['Organization'] = {
	onload: function(listview) {
		if (listview.page.fields_dict.parent_organization) {
			listview.page.fields_dict.parent_organization.get_query = function() {
				return {
					"filters": {
						"is_group": ["=", 1],
					}
				};
			};
		}
	}
};
