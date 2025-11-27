import frappe


def execute():
	settings = frappe.get_single("System Settings")
	settings.update(
		{
			"apply_perm_level_on_api_calls": 1,
			"disable_document_sharing": 1,
			"allow_older_web_view_links": 0,
		}
	)
	settings.save()
