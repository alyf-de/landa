import frappe


def execute():
	"""Create a letter head for each company.

	The old letter head was computed dynamically from the doc's company. This doesn't work for printing reports, so we need to create a letter head for each company.
	"""
	frappe.local.lang = "de"
	old_letter_head = frappe.get_doc("Letter Head", "Extended Information in Footer")
	for company in frappe.get_all(
		"Company",
		filters={"name": ("!=", "Landesverband Sächsischer Angler")},
		pluck="name",
	):
		new_letter_head = frappe.new_doc("Letter Head")
		new_letter_head.custom_company = company
		new_letter_head.letter_head_name = company
		new_letter_head.footer = frappe.render_template(
			old_letter_head.footer, {"doc": frappe._dict(company=company)}
		).strip()
		new_letter_head.save()
		frappe.db.set_value("Company", company, "default_letter_head", new_letter_head.name)
