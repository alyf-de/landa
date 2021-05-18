import frappe
from frappe import get_hooks


def after_install():
	create_records_from_hooks()


def create_records_from_hooks():
	records = get_hooks('landa_create_after_install')
	for record in records:
		try:
			doc = frappe.get_doc(record)
			doc.save()
		except frappe.DuplicateEntryError:
			continue
