frappe.listview_settings['Catch Log Entry'] = {
	onload: function(listview) {
		if (listview.page.fields_dict.regional_organization) {
			listview.page.fields_dict.regional_organization.get_query = function() {
				return {
					"filters": {
						"name": ["in", ["AVL", "AVS", "AVE"]],
					}
				};
			};
		}
	}
};
