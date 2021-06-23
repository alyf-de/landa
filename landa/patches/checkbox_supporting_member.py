import frappe


def execute():
	"""Convert select field with options ('', 'Fördermitglied') to checkbox 'Is Supporting Member'."""
	members = frappe.db.get_all("Member", filters={"member_type": "Fördermitglied"}, pluck="name")
	frappe.reload_doc("organization_management", "doctype", "member")

	for member in members:
		frappe.set_value("Member", member, "is_supporting_member", 1)
