import frappe
from frappe.custom.doctype.property_setter.property_setter import delete_property_setter
from frappe.query_builder.functions import IfNull

ITEM_DOCTYPES = ("Delivery Note Item", "Sales Invoice Item")


def execute():
	"""Move the free-text serial numbers from ERPNext's `serial_no` into our own field.

	Since v15, ERPNext hides `serial_no` unless "Use Serial No / Batch Fields" is enabled.
	"""
	for doctype in ITEM_DOCTYPES:
		delete_property_setter(doctype, property="columns", field_name="serial_no")

		# MariaDB evaluates the assignments from left to right, so the value is copied before it is cleared.
		item = frappe.qb.DocType(doctype)
		(
			frappe.qb.update(item)
			.set(item.custom_serial_numbers, item.serial_no)
			.set(item.serial_no, None)
			.where(IfNull(item.serial_no, "") != "")
		).run()
