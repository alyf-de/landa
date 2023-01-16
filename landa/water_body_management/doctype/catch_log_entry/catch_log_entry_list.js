frappe.listview_settings["Catch Log Entry"] = {
	onload(listview) {
		landa.utils.setup_regional_organization_filter(listview, "regional_organization");
	},
};
