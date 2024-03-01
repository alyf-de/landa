import frappe
from frappe.model.rename_doc import rename_doc


def execute():
	"""Adjust the existing External Contacts to link to the regional organization
	instead of the organization.

	Also change the name of the External Contacts to reflect the new organization.
	"""
	for external_contact, organization in frappe.get_all(
		"External Contact",
		filters={"organization": ("is", "set")},
		fields=["name", "organization"],
		as_list=True,
	):
		regional_organization = frappe.get_doc("Organization", organization[:3])
		ext_contact = frappe.get_doc("External Contact", external_contact)
		ext_contact.db_set(
			{
				"organization": regional_organization.name,
				"organization_name": regional_organization.organization_name,
			},
			update_modified=False,
		)
		ext_contact.autoname()
		rename_doc(
			"External Contact",
			external_contact,
			external_contact.replace(organization, regional_organization.name),
			force=True,
			show_alert=False,
		)
