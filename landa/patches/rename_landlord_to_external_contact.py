from frappe.model.utils.rename_field import rename_field


def execute():
	rename_field("Lease Contract", "landlord", "external_contact")
