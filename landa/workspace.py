from frappe.desk.doctype.workspace.workspace import Workspace


def validate(doc: Workspace, method=None) -> None:
	# Custom reports (possibly of other users) should not be visible
	if doc.for_user and doc.hide_custom == 0:
		doc.hide_custom = 1
