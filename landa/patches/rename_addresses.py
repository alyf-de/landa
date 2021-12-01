
import frappe
from frappe.utils import update_progress_bar

from landa.organization_management.address.address import autoname


def execute():
	doctype = "Address"
	all_addresses = frappe.get_all(doctype)
	total_addresses = len(all_addresses)

	for counter, address in enumerate(all_addresses):
		update_progress_bar('Renaming Addresses', counter, total_addresses)
		doc = frappe.get_doc(doctype, address.name)

		old_name = address.name
		autoname(doc, None)	 # changes doc.name to the new name
		new_name = doc.name

		if new_name[-2:] == "-1":
			new_name = new_name[:-2]

		if old_name == new_name:
			continue

		try:
			frappe.rename_doc(doctype, old_name, new_name)
		except frappe.exceptions.ValidationError:
			pass

		if counter > 0 and counter % 100 == 0:
			frappe.db.commit()
