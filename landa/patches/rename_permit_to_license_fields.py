import frappe

RENAMED_FIELDS = {
	"permit_is_valid_for_life": "license_is_valid_for_life",
	"permit_issue_date": "license_issue_date",
	"permit_expiration_date": "license_expiration_date",
}


def execute():
	"""Copy data from the old permit_* columns to the new license_* columns."""
	# Fresh installs never had the old columns
	if not frappe.db.has_column("LANDA Member", "permit_issue_date"):
		return

	member = frappe.qb.DocType("LANDA Member")
	query = frappe.qb.update(member)
	for old_fieldname, new_fieldname in RENAMED_FIELDS.items():
		query = query.set(member[new_fieldname], member[old_fieldname])

	query.run()
