frappe.listview_settings["Stocking Measure"] = {
	get_indicator: function (doc) {
		const status_color = {
			Draft: "red",
			"In Progress": "blue",
			Completed: "green",
		};

		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
	refresh: function (doc) {
		doc.page.add_actions_menu_item(
			__("Create Stocking Targets"),
			() => showCreateStockingTargetsDialog(),
			false
		); // Needs to be in refresh, otherwise it won't work in the Report View
	},
};

function showCreateStockingTargetsDialog() {
	const dialog = new frappe.ui.Dialog({
		title: __("Create Stocking Targets"),
		fields: [
			{
				label: __("Year"),
				fieldname: "year",
				fieldtype: "Int",
				reqd: 1,
				description: __(
					"Based on your selection, Stocking Targets are created accordingly for the specified year."
				),
			},
		],
		size: "small",
		primary_action_label: __("Create"),
		primary_action(values) {
			const selected_measures = cur_list.get_checked_items(true);

			frappe.call({
				method: "landa.water_body_management.doctype.stocking_measure.stocking_measure.create_stocking_targets",
				args: {
					stocking_measure_names: selected_measures,
					year: values.year,
				},
				callback: function (response) {
					frappe.set_route("List", "Stocking Target", "List");
				},
			});

			dialog.hide();
		},
	});

	dialog.show();
}
