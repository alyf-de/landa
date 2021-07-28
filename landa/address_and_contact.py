import frappe

def has_permission(doc, ptype, user):
	for link in doc.links:
		linked_doc = frappe.get_doc(link.link_doctype, link.link_name)
		if frappe.has_permission(link.link_doctype, ptype=ptype, doc=linked_doc, user=user):
			return True

	return False
