import frappe

from landa.workspace import LANDA_WORKSPACES


def execute():
	"""Hide custom reports in existing customized landa workspaces."""
	for workspace in frappe.get_all(
		"Workspace",
		filters={
			"for_user": ("is", "set"),
			"hide_custom": 0,
			"extends": ("in", LANDA_WORKSPACES),
		},
		pluck="name",
	):
		frappe.db.set_value("Workspace", workspace, "hide_custom", 1)
