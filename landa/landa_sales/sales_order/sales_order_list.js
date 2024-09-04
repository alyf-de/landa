if (!frappe.listview_settings["Sales Order"].formatters) {
	frappe.listview_settings["Sales Order"].formatters = {};
}

frappe.listview_settings["Sales Order"].formatters.name = (value) => value.slice(9);
