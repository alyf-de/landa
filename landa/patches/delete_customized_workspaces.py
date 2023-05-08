import frappe


def execute():
	custom_workspaces = frappe.get_all(
		"Workspace",
		filters={"for_user": ("is", "set"), "extends": ("is", "set")},
		pluck="name",
	)
	for workspace_name in custom_workspaces:
		# Delete user customized workspaces that extend standard workspaces
		frappe.delete_doc("Workspace", workspace_name)
