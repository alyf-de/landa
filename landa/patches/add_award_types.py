import frappe


def execute():
	add_award_typyes()


def add_award_typyes():
	award_types = [
		"Goldene Äsche",
		"Ehrennadel Bronze",
		"Ehrennadel Silber",
		"Ehrennadel Gold",
		"Ehrennadel VGA Bronze",
		"Ehrennadel VGA Silber",
		"Ehrennadel VGA Gold",
		"Jugendmedaille",
		"Hegemedaille",
		"Ehrenurkunde",
		"Ehrenplakette",
		"Ehrenspange",
		"Ehrenpokal",
	]

	for award_type in award_types:
		if not frappe.db.exists("Award Type", award_type):
			doc = frappe.get_doc(
				{
					"doctype": "Award Type",
					"award_type": award_type,
				}
			)
			doc.insert()
