import frappe


def execute():
	"""
	UOM became mandatory in Item Price, so far it was empty.
	This patch updates all Item Prices to use the UOM "Anzahl".
	"""
	frappe.qb.update("Item Price").set("uom", "Anzahl").run()
