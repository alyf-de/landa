frappe.listview_settings["Lease Contract"] = {
	onload: function (listview) {
		landa.utils.setup_regional_organization_filter(listview, "organization");
	},
};
