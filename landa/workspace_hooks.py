import frappe

def validate_workspace(doc, method):
    if doc.doctype == "Workspace":
        if doc.hide_custom == 0:
            doc.hide_custom = 1
            frappe.msgprint("Die Checkbox 'Hide Custom' wurde automatisch auf 1 gesetzt.")
