frappe.listview_settings["Fishing Area"] = {
	onload(listview) {
		landa.utils.setup_regional_organization_filter(listview, "organization");
	},
};
