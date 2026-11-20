import frappe


def execute():
	"""Let all desk users read public notes and mark them as seen.

	A Custom DocPerm for "System Manager" only replaced the standard Note permissions.
	The standard ones already hide the "Seen By" table from regular users.
	"""
	frappe.db.delete("Custom DocPerm", {"parent": "Note"})
	frappe.clear_cache(doctype="Note")
