if (!frappe.listview_settings["Sales Invoice"].formatters) {
	frappe.listview_settings["Sales Invoice"].formatters = {};
}

frappe.listview_settings["Sales Invoice"].formatters.name = (value) => value.slice(9);
