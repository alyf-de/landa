import frappe


def execute():
	for abbr in ("AVS", "AVL", "AVE"):
		frappe.db.set_value(
			"Customer",
			{"default_price_list": ("is", "not set"), "name": ("like", f"{abbr}-%")},
			"default_price_list",
			f"Standard - {abbr}",
			update_modified=False,
		)
