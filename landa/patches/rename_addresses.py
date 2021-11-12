
import frappe
from landa.organization_management.address.address import autoname


def execute():
	doctype = "Address"
	for address in frappe.get_all(doctype):
		doc = frappe.get_doc(doctype, address.name)

		old_name = address.name
		autoname(doc, None)	 # changes doc.name to the new name
		new_name = doc.name

		if new_name[-2:] == "-1":
			new_name = new_name[:-2]

		if old_name == new_name:
			continue

		frappe.rename_doc(doctype, old_name, new_name)
