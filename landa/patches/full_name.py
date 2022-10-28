import frappe
from landa.organization_management.doctype.landa_member.landa_member import (
	get_full_name,
)


def execute():
	"""
	Run landa.address_and_contact.validate for all existing addresses and
	contacts.
	"""
	frappe.reload_doctype("LANDA Member")

	all_names = frappe.get_all(
		"LANDA Member", fields=["name", "first_name", "last_name"], as_list=1
	)
	for name, first_name, last_name in all_names:
		frappe.set_value(
			"LANDA Member", name, "full_name", get_full_name(first_name, last_name)
		)
