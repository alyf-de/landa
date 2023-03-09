import frappe
from frappe import _

from frappe.desk.form.document_follow import follow_document
from frappe.share import get_share_name, notify_assignment
from frappe.utils import cint


@frappe.whitelist()
def add(
	doctype, name, user=None, read=1, write=0, submit=0, share=0, everyone=0, flags=None, notify=0
):
	"""Share the given document with a user."""
	if not user:
		user = frappe.session.user

	if not (flags or {}).get("ignore_share_permission"):
		frappe.throw(_("Not permitted to share {0}").format(doctype))

	share_name = get_share_name(doctype, name, user, everyone)

	if share_name:
		doc = frappe.get_doc("DocShare", share_name)
	else:
		doc = frappe.new_doc("DocShare")
		doc.update(
			{"user": user, "share_doctype": doctype, "share_name": name, "everyone": cint(everyone)}
		)

	if flags:
		doc.flags.update(flags)

	doc.update(
		{
			# always add read, since you are adding!
			"read": 1,
			"write": cint(write),
			"submit": cint(submit),
			"share": cint(share),
		}
	)

	doc.save(ignore_permissions=True)
	notify_assignment(user, doctype, name, everyone, notify=notify)

	follow_document(doctype, name, user)

	return doc
