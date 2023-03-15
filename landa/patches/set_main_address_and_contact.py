import frappe


def execute():
	for doctype in ("Address", "Contact"):
		organization_addresses = frappe.get_all(
			"Dynamic Link",
			filters={
				"link_doctype": "Organization",
				"link_name": ("is", "set"),
				"parenttype": doctype,
			},
			pluck="parent",
			distinct=True,
		)
		table = frappe.qb.DocType(doctype)
		frappe.qb.update(table).set(table.belongs_to_organization, 1).where(
			table.name.isin(organization_addresses)
		).run()
