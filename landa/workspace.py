import frappe


def validate_workspace(doc, method):
	if (
		doc.for_user and
		doc.hide_custom == 0 and
		doc.extends in ("Water Body Management", "Organization Management", "Order Management")
	):
		doc.hide_custom = 1
