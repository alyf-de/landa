import frappe
from frappe import get_hooks


def after_install():
	create_records_from_hooks()
	disable_modes_of_payment()


def create_records_from_hooks():
	records = get_hooks('landa_create_after_install')
	for record in records:
		try:
			doc = frappe.get_doc(record)
			doc.save()
		except frappe.DuplicateEntryError:
			continue

def disable_modes_of_payment():
	names = get_hooks('disable_modes_of_payment')
	for name in names:
		try:
			doc = frappe.set_value('Mode of Payment', name, 'enabled', False)
		except frappe.DoesNotExistError:
			continue
