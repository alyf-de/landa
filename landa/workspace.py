from frappe.desk.doctype.workspace.workspace import Workspace

LANDA_WORKSPACES = (
	"Water Body Management",
	"Organization Management",
	"Order Management",
)


def validate(doc: Workspace, method=None) -> None:
	# Custom reports (possibly of other users) should not be visible
	if doc.for_user and doc.hide_custom == 0 and doc.extends in LANDA_WORKSPACES:
		doc.hide_custom = 1
