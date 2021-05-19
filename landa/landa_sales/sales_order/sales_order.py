# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.data import get_year_ending

def before_validate(delivery_note, event):
	for item in delivery_note.items:
		item.delivery_date = get_year_ending(str(delivery_note.year_of_settlement))

@frappe.whitelist()
def get_items(year):
	"""Return all Items that are always valid of in the specified year."""
	fields = ['item_code', 'item_name', 'cannot_be_returned', 'description', 'stock_uom as uom']
	items = frappe.get_list('Item',
		filters={
			'valid_from_year': ["<=", year],
			'valid_to_year': [">=", year],
			'has_variants': False,
			'cannot_be_ordered': False
		},
		fields=fields,
	)

	for item in items:
		item.qty = 0
		item.uom_factor = 1
		item.rate = 1 # TODO: Set correct rate.

	return items
