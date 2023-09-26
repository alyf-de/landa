import frappe
from frappe import _


def create_version_log(doc, event):
	"""Called via hooks.py to create Version Log of document creation"""
	if doc.doctype == "File" and doc.attached_to_doctype != "Water Body":
		return

	doc.flags.updater_reference = {
		"doctype": doc.doctype,
		"docname": doc.name,
		"event": "Created",
		"label": _(f"{doc.doctype} {doc.name} Created"),
	}

	doc._doc_before_save = None
