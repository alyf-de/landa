import frappe
from frappe.custom.doctype.property_setter.property_setter import delete_property_setter

ITEM_DOCTYPES = ("Delivery Note Item", "Sales Invoice Item")


def execute():
	"""Move the free-text serial numbers from ERPNext's `serial_no` into our own field.

	Since v15, ERPNext hides `serial_no` unless "Use Serial No / Batch Fields" is enabled.
	"""
	for doctype in ITEM_DOCTYPES:
		delete_property_setter(doctype, property="columns", field_name="serial_no")
		frappe.db.sql(f"""
			UPDATE `tab{doctype}`
			SET custom_serial_numbers = serial_no,
				serial_no = NULL
			WHERE IFNULL(serial_no, '') != ''
		""")
