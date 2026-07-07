import frappe


def onload(doc, event):
	if doc.organization:
		doc.set_onload("active_member_functions", get_active_member_functions(doc.organization))


def get_active_member_functions(organization: str) -> list[dict]:
	if not frappe.has_permission("Member Function"):
		return []

	return frappe.get_list(
		"Member Function",
		filters={"organization": organization, "status": "Active"},
		fields=[
			"name",
			"member_function_category",
			"member",
			"member_first_name",
			"member_last_name",
			"start_date",
		],
		order_by="member_function_category asc",
	)
