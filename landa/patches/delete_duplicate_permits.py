import frappe
from frappe.utils import update_progress_bar


def execute():
	duplicates = frappe.db.sql("""
		SELECT
			member,
			year,
			type,
			docstatus,
			number,
			COUNT(*) AS occurrence_count
		FROM `tabYearly Fishing Permit`
		WHERE member IS NOT NULL AND member != ''
		GROUP BY member, year, type, docstatus, number
		HAVING COUNT(*) > 1
		ORDER BY year DESC;
	""")

	print(f"Found {len(duplicates)} duplicate permits")

	total = len(duplicates)
	for i, (member, year, type, docstatus, number, _count) in enumerate(duplicates):
		update_progress_bar("Deleting duplicate permits", i, total)

		keep = frappe.db.get_value(
			"Yearly Fishing Permit",
			filters={
				"member": member,
				"year": year,
				"type": type,
				"docstatus": docstatus,
				"number": number,
			},
			order_by="creation ASC",
		)

		frappe.db.delete(
			"Yearly Fishing Permit",
			{
				"name": ("!=", keep),
				"member": member,
				"year": year,
				"type": type,
				"docstatus": docstatus,
				"number": number,
			},
		)
