import frappe


def execute():
	cleanup_addresses()
	cleanup_contacts()


def cleanup_addresses():
	# the two checkboxes are no longer used and are hidden from now on.
	# nosemgrep
	frappe.db.sql("""update `tabAddress` set is_shipping_address=0, is_primary_address=0""")


def cleanup_contacts():
	# the two checkboxes are no longer used and are hidden from now on.
	# nosemgrep
	frappe.db.sql("""update `tabContact` set is_billing_contact=0, is_primary_contact=0""")
