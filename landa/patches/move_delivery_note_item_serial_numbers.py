import frappe


def execute():
	frappe.db.sql("""
		UPDATE `tabDelivery Note Item`
		SET custom_serial_numbers = serial_no,
			serial_no = NULL
		WHERE serial_no IS NOT NULL
			AND serial_no != ''
	""")
