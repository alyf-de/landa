import frappe
from frappe.utils import update_progress_bar

from landa.organization_management.contact.contact import (
	set_primary_email_if_missing,
	set_primary_phone_if_missing,
)


def execute():
	frappe.db.auto_commit_on_many_writes = True

	contacts = frappe.get_all(
		"Contact",
		or_filters={
			"phone": ("is", "not set"),
			"mobile_no": ("is", "not set"),
			"email_id": ("is", "not set"),
		},
		pluck="name",
	)
	total = len(contacts)
	for i, contact_name in enumerate(contacts):
		update_progress_bar("Setting primary email and phone", i, total)
		contact = frappe.get_doc("Contact", contact_name)
		modified = set_primary_email_if_missing(contact)
		modified |= set_primary_phone_if_missing(contact)
		if modified:
			contact.save(ignore_permissions=True, ignore_version=True)

	frappe.db.auto_commit_on_many_writes = False
