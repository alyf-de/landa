frappe.listview_settings['Fishing Area'] = {
	onload: function(listview) {
		if (listview.page.fields_dict.organization) {
			listview.page.fields_dict.organization.get_query = function() {
				return {
					"filters": {
						"name": ["in", ["AVL", "AVS", "AVE"]],
					}
				};
			};
		}
	}
};
