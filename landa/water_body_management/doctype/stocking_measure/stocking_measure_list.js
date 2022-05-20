frappe.listview_settings["Stocking Measure"] = {
	get_indicator: function (doc) {
		var status_color = {
			Draft: "red",
			"In Progress": "blue",
			Completed: "green",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};
