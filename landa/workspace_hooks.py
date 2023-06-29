import frappe

if doc.doctype == "Workspace":
	if doc.hide_custom == 0:
		doc.hide_custom = 1
		frappe.msgprint("Die Checkbox 'Hide Custom' wurde automatisch auf 1 gesetzt.")
		if (
			doc.for_user
			and doc.hide_custom == 0
			and doc.extends in ("Water Body Management", "Organization Management", "Order Management")
		):
			doc.hide_custom = 1
