import frappe
from frappe import get_hooks


def after_install():
	create_records_from_hooks()
	disable_modes_of_payment()
	add_session_defaults()
	setup_uoms()


def create_records_from_hooks():
	records = get_hooks('landa_create_after_install', default=[], app_name='landa')
	for record in records:
		try:
			doc = frappe.get_doc(record)
			doc.save()
		except frappe.DuplicateEntryError:
			continue


def disable_modes_of_payment():
	names = get_hooks('disable_modes_of_payment', default=[], app_name='landa')
	for name in names:
		try:
			frappe.set_value('Mode of Payment', name, 'enabled', False)
		except frappe.DoesNotExistError:
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


def setup_uoms():
	# create new UOM "Anzahl"
	if not frappe.db.exists("UOM", "Anzahl"):
		doc = frappe.new_doc("UOM")
		doc.uom_name = "Anzahl"
		doc.insert()

	# Disable all other UOMs
	uom_table = frappe.qb.DocType("UOM")
	frappe.qb.update(uom_table).set(uom_table.enabled, 0).where(
		uom_table.uom_name != "Anzahl"
	).run()
