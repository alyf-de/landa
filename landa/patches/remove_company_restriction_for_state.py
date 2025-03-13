import frappe


def execute():
	"""For state organization employees, remove the User Permission that restricted them on one company."""
	users = frappe.get_all(
		"User",
		filters=[
			["Has Role", "role", "=", "LANDA State Organization Employee"],
		],
		pluck="name",
	)
	frappe.db.delete(
		"User Permission",
		{
			"user": ("in", users),
			"allow": "Company",
		},
	)
