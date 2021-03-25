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
	fields: [
		{
			fieldtype: 'Check',
			fieldname: 'is_group',
			label: __('Is Group'),
			description: __("Can contain suborganizations")
		},
		{
			fieldtype: 'Data',
			fieldname: 'organization_name',
			label: __('Organization Name'),
			reqd: 1,
			description: __('Full name of the organization. For example, "Landesverband Sächsischer Angler e.V."')
		},
		{
			fieldtype: 'Data',
			fieldname: 'short_code',
			length: 4,
			depends_on: 'is_group',
			label: __('Short Code'),
			description: __('Short code for regional organizations. For example, "LVSA", "AVL", etc.')
		}
	],
	root_label: "All Organizations",
	get_tree_root: false,
	onload: function(treeview) {
		treeview.make_tree();
	}
};