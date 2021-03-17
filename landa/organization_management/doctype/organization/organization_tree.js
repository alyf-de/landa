frappe.treeview_settings["Organization"] = {
	ignore_fields: ["parent_organization"],
	get_tree_nodes: 'landa.organization_management.doctype.organization.organization.get_children',
	add_tree_node: 'landa.organization_management.doctype.organization.organization.add_node',
	filters: [
		{
			fieldname: "organization",
			fieldtype: "Link",
			options: "Organization",
			label: __("Organization"),
			get_query: function() {
				return {
					filters: [["Organization", 'is_group', '=', 1]]
				};
			}
		},
	],
	root_label: "All Organizations",
	get_tree_root: false,
	onload: function(treeview) {
		treeview.make_tree();
	}
};