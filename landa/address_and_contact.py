import frappe

def has_permission(doc, ptype, user):
	if not doc.links and not frappe.db.get_single_value("System Settings", "apply_strict_user_permissions"):
		# No links and strict user permissions disabled
		return True

	for link in doc.links:
		linked_doc = frappe.get_doc(link.link_doctype, link.link_name)
		if frappe.has_permission(link.link_doctype, ptype=ptype, doc=linked_doc, user=user):
			# We have permission on one linked doc
			return True

	# There are linked docs but we don't have permission on any of them
	return False
