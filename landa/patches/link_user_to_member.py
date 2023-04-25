import frappe

from landa.install import make_custom_fields, make_property_setters, update_system_settings


def create_docperm():
	"""This custom docperm needs to exist so that User Permissions on User will work as expected."""
	docperm = frappe.new_doc("Custom DocPerm")
	docperm.parent = "User"
	docperm.role = "All"
	docperm.select = 1
	docperm.read = 0
	docperm.export = 0
	docperm.save()


def execute():
	update_system_settings()
	make_custom_fields()
	make_property_setters()
	create_docperm()

	for member, user, organization in frappe.get_all(
		"LANDA Member",
		filters={"user": ("is", "set")},
		fields=["name", "user", "organization"],
		as_list=True,
	):
		doc = frappe.get_doc("User", user)
		doc.update(
			{
				"landa_member": member,
				"organization": organization,
				"allowed_in_mentions": 0,
			}
		)
		doc.save()
