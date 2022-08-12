import frappe


def execute():
	frappe.reload_doctype("Yearly Fishing Permit")

	frappe.db.sql("""
		UPDATE `tabYearly Fishing Permit`
		LEFT JOIN `tabLANDA Member`
		ON `tabYearly Fishing Permit`.`member` = `tabLANDA Member`.`name`

		SET
			`tabYearly Fishing Permit`.`first_name` = `tabLANDA Member`.`first_name`,
			`tabYearly Fishing Permit`.`last_name` = `tabLANDA Member`.`last_name`
	""")
