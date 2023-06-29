import frappe


def execute():
	workspaces = frappe.get_all(
		"Workspace",
		filters={
			"for_user": ["is", "set"],
			"hide_custom": 0,
			"extends": ["in", ["Water Body Management", "Organization Management", "Order Management"]],
		},
	)

	for workspace in workspaces:
		doc = frappe.get_doc("Workspace", workspace.name)
		doc.hide_custom = 1
		doc.save()
