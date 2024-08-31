if (!frappe.listview_settings["Delivery Note"].formatters) {
	frappe.listview_settings["Delivery Note"].formatters = {};
}

frappe.listview_settings["Delivery Note"].formatters.name = (value) => {
	if (value.startsWith("RET")) {
		return value.slice(8);
	} else {
		return value.slice(9);
	}
};
