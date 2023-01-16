frappe.listview_settings["Water Body"] = {
	onload: function (listview) {
		landa.utils.setup_regional_organization_filter(listview, "organization");
	},
};
