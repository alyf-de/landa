import frappe


def execute():
    frappe.db.set_value(
        dt="System Settings",
        dn="System Settings",
        field={
            "apply_perm_level_on_api_calls": 1,
            "disable_document_sharing": 1
        }
    )
