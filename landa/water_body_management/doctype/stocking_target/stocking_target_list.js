frappe.listview_settings["Stocking Target"] = {
	get_indicator: function (doc) {
		const status_color = {
			Draft: "red",
			"In Progress": "blue",
			Completed: "green",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};
