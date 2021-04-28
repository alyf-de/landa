# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.data import today

@frappe.whitelist()
def get_items(year):
	"""Return all Items that are always valid of in the specified year."""
	fields = ['item_code', 'item_name', 'cannot_be_returned', 'description']
	items = frappe.get_list('Item',
		filters={
			'valid_to_year': ["<=", year],
			'valid_from_year': [">=", year],
			'has_variants': False
		},
		fields=fields,
	)

	items.extend(frappe.get_list('Item',
		filters={
			'valid_to_year': 0,
			'valid_from_year': 0,
			'has_variants': False
		},
		fields=fields,
	))

	for item in items:
		item.delivery_date = today()
		item.qty = 0
		item.uom = 'Nos'
		item.uom_factor = 1
		item.rate = 1 # TODO: Set correct rate.

	return items
