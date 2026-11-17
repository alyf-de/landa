import frappe


def execute():
	"""Move the former single Stocking Site link of Stocking Measure into the new table."""
	if not frappe.db.has_column("Stocking Measure", "stocking_site"):
		return

	stocking_measure = frappe.qb.DocType("Stocking Measure")
	measures = (
		frappe.qb.from_(stocking_measure)
		.select(stocking_measure.name, stocking_measure.stocking_site)
		.where(stocking_measure.stocking_site.isnotnull())
		.where(stocking_measure.stocking_site != "")
		.run(as_dict=True)
	)
	for measure in measures:
		frappe.get_doc(
			{
				"doctype": "Stocking Measure Site",
				"parenttype": "Stocking Measure",
				"parent": measure.name,
				"parentfield": "stocking_sites",
				"idx": 1,
				"stocking_site": measure.stocking_site,
			}
		).db_insert()
