frappe.listview_settings['Water Body Management Local Organization'] = {
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
