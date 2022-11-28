import frappe


def execute():
	table = frappe.qb.DocType("Translation")
	frappe.qb.from_(table).delete().where(table.language == "de").run()


def move_translations_csv():
	"""Move translations from Translation DocType into CSV file.

	Executed manually in dev environment.
	"""
	from csv import writer
	from os.path import join as join_path
	from frappe import get_app_path

	with open(join_path(get_app_path("landa"), "translations/de.csv"), "w") as f:
		writer(f).writerows(
			frappe.get_all(
				"Translation",
				fields=["source_text", "translated_text"],
				filters={"language": "de"},
				order_by="source_text ASC",
				as_list=True,
			)
		)
