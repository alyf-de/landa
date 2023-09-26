import frappe


def execute():
	for c in frappe.get_all("Lease Contract", fields=["name", "rent_per_month"]):
		if not c.rent_per_month:
			continue

		frappe.db.set_value("Lease Contract", c.name, "rent_per_year", c.rent_per_month * 12)
