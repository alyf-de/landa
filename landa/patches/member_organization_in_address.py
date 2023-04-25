import frappe
from frappe.utils import update_progress_bar

from landa.address_and_contact import validate


def execute():
	"""Update links in all Address and Contact documents linked to a member of a local group.

	Organization in Address and contact used to link to the Local Organization.
	Now it should lik to either the Local Group or the Local Organization.
	"""
	addresses_to_update = frappe.get_all(
		"Address",
		filters=[
			# members with four dashes in the name are in a local group, for example: AVS-001-01-0001
			["Dynamic Link", "link_name", "like", "%-%-%-%"],
			["Dynamic Link", "link_doctype", "=", "LANDA Member"],
		],
		pluck="name",
	)
	total_lenth = len(addresses_to_update)
	for i, adress_name in enumerate(addresses_to_update):
		update_progress_bar("Updating Addresses", i, total_lenth)
		doc = frappe.get_doc("Address", adress_name)
		validate(doc, "patch")
		doc.save(ignore_permissions=True)
