import frappe

from landa.organization_management.doctype.landa_member.landa_member import get_full_name
from landa.utils import autocommit


def execute():
	"""
	Run landa.address_and_contact.validate for all existing addresses and
	contacts.
	"""
	frappe.reload_doctype("LANDA Member")

	with autocommit():
		for name, first_name, last_name in frappe.get_all(
			"LANDA Member",
			fields=["name", "first_name", "last_name"],
			filters={"full_name": ("is", "not set")},
			as_list=1,
		):
			frappe.db.set_value(
				"LANDA Member",
				name,
				"full_name",
				get_full_name(first_name, last_name),
				update_modified=False,
			)
