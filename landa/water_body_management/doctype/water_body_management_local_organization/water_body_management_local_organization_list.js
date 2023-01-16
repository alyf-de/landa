frappe.listview_settings["Water Body Management Local Organization"] = {
	onload: function (listview) {
		landa.utils.setup_regional_organization_filter(listview, "regional_organization");
	},
};
