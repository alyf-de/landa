// Initialize listview settings without overwriting potentially existing settings
frappe.listview_settings["Report"] = frappe.listview_settings["Report"] || {};
frappe.listview_settings["Report"].filters =
	frappe.listview_settings["Report"].filters || [];

// add a default filter
frappe.listview_settings["Report"].filters.push(["is_standard", "=", "No"]);
