import frappe
from frappe.utils import update_progress_bar

from landa.utils import autocommit


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
		WHERE member IS NOT NULL AND member != '' AND docstatus != 2
		GROUP BY member, year, type, docstatus, number
		HAVING COUNT(*) > 1
		ORDER BY year DESC;
	""")

	print(f"Found {len(duplicates)} duplicate permits")

	total = len(duplicates)
	for i, (member, year, permit_type, docstatus, number, _count) in enumerate(duplicates):
		update_progress_bar("Deleting duplicate permits", i, total)

		record_to_keep = frappe.db.get_value(
			"Yearly Fishing Permit",
			filters={
				"member": member,
				"year": year,
				"type": permit_type,
				"docstatus": docstatus,
				"number": number,
			},
			order_by="creation ASC",
		)

		records_to_delete = frappe.get_all(
			"Yearly Fishing Permit",
			filters={
				"name": ("!=", record_to_keep),
				"member": member,
				"year": year,
				"type": permit_type,
				"docstatus": docstatus,
				"number": number,
			},
			fields=["name", "docstatus"],
		)

		with autocommit():
			for record in records_to_delete:
				if record.docstatus == 1:
					frappe.get_doc("Yearly Fishing Permit", record.name).cancel()
				else:
					frappe.delete_doc(
						"Yearly Fishing Permit",
						record.name,
						ignore_permissions=True,
						ignore_missing=True,
					)
