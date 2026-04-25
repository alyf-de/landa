import frappe


def before_validate(item_price, event):
	if _is_erpnext_test_item_price(item_price) and item_price.uom == "Anzahl":
		item_price.uom = frappe.db.get_value("Item", item_price.item_code, "stock_uom")


def validate(item_price, event):
	"""
	Unset any values that might have been set by accident and will mess up pricing logic.

	For example, customer gets set automatically if it is set in session defaults. We need to unset it again.
	See https://github.com/frappe/frappe/issues/14290
	"""
	# ERPNext test records link to _Test Items with their own fixture UOMs.
	if _is_erpnext_test_item_price(item_price):
		return

	item_price.customer = ""
	item_price.supplier = ""
	item_price.uom = "Anzahl"
	item_price.batch_no = ""
	item_price.lead_time_days = 0


def _is_erpnext_test_item_price(item_price):
	return frappe.flags.in_test and item_price.item_code and item_price.item_code.startswith("_Test")
