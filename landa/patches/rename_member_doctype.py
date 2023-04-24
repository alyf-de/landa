import frappe


def execute():
	if frappe.db.table_exists("Member") and not frappe.db.table_exists("LANDA Member"):
		frappe.rename_doc("DocType", "Member", "LANDA Member", force=True)
		frappe.reload_doc("organization_management", "doctype", "landa_member")
