import frappe

from landa.install import make_property_setters
from landa.property_setters import get_property_setters


def execute():
	make_property_setters()

	for doctype, setters in get_property_setters().items():
		if not any(field == "group_same_items" for field, _property, _value in setters):
			continue
		if not frappe.db.exists("DocType", doctype):
			continue
		if not frappe.db.has_column(doctype, "group_same_items"):
			continue

		doctype_table = frappe.qb.DocType(doctype)
		(
			frappe.qb.update(doctype_table)
			.set(doctype_table.group_same_items, 0)
			.where((doctype_table.group_same_items == 1) & (doctype_table.docstatus == 0))
		).run()
