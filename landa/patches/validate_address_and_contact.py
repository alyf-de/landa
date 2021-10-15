
import frappe

def execute():
	"""
	Run landa.address_and_contact.validate for all existing addresses and
	contacts.
	"""
	for dt in ["Address", "Contact"]:
		frappe.reload_doctype(dt)

		all_names = frappe.get_all(dt, pluck="name")
		for name in all_names:
			doc = frappe.get_doc(dt, name)
			doc.save()
