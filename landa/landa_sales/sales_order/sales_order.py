# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from frappe.utils.data import get_year_ending

def before_validate(delivery_note, event):
	for item in delivery_note.items:
		item.delivery_date = get_year_ending(str(delivery_note.year_of_settlement))
