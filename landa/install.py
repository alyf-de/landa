import frappe
from frappe import get_hooks


def after_install():
	create_records_from_hooks()
	add_session_defaults()


def create_records_from_hooks():
	records = get_hooks('landa_create_after_install', default=[], app_name='landa')
	for record in records:
		try:
			doc = frappe.get_doc(record)
			doc.save()
		except frappe.DuplicateEntryError:
			continue


def add_session_defaults():
	settings = frappe.get_single('Session Default Settings')
	ref_doctypes = get_hooks('landa_add_to_session_defaults', default=[], app_name='landa')
	existing_ref_doctypes = [row.ref_doctype for row in settings.session_defaults]

	for ref_doctype in ref_doctypes:
		if ref_doctype in existing_ref_doctypes:
			continue

		settings.append("session_defaults", {
			"ref_doctype": ref_doctype
		})

	settings.save()
