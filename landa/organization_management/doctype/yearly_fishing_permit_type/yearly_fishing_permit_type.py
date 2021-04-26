# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class YearlyFishingPermitType(Document):
	def before_insert(self):
		self.short_code = self.short_code.upper()

	def on_submit(self):
		add_attribute_value(
			"Erlaubnisscheinart",
			self.yearly_fishing_permit_type_name,
			self.short_code
		)

def add_attribute_value(name, attribute_value, abbr):
	create_item_attribute(name)
	item_attr = frappe.get_doc("Item Attribute", name)
	item_attr.append('item_attribute_values', {
		'attribute_value': attribute_value,
		'abbr': abbr
	})
	item_attr.save()


def create_item_attribute(name):
	"""Create an Item Attribute if there isn't one already"""
	if not frappe.db.exists("Item Attribute", name):
		item_attr = frappe.new_doc("Item Attribute")
		item_attr.attribute_name = name
		item_attr.insert()
