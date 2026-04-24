import frappe

from .custom_fields import get_custom_fields
from .doc_perms import get_doc_perms
from .property_setters import get_property_setters


def before_uninstall():
	remove_custom_fields()
	remove_property_setters()
	remove_doc_perms()


def remove_custom_fields():
	print("* removing custom fields...")
	for doctypes, custom_fields in get_custom_fields().items():
		if isinstance(doctypes, str):
			doctypes = (doctypes,)

		for doctype in doctypes:
			for cf in custom_fields:
				frappe.db.delete(
					"Custom Field",
					{
						"dt": doctype,
						"fieldname": cf.get("fieldname"),
					},
				)


def remove_property_setters():
	print("* removing property setters...")
	for doctypes, property_setters in get_property_setters().items():
		if isinstance(doctypes, str):
			doctypes = (doctypes,)

		for doctype in doctypes:
			for ps in property_setters:
				frappe.db.delete(
					"Property Setter",
					{
						"doc_type": doctype,
						"field_name": ps[0],
						"property": ps[1],
						"value": ps[2],
					},
				)


def remove_doc_perms():
	print("* removing custom doc perms...")
	for doctype in get_doc_perms():
		frappe.db.delete("Custom DocPerm", {"parent": doctype})
