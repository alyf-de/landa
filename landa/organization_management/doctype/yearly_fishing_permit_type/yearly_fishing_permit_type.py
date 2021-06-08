# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import get_link_to_form
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
	item_attr_link = get_link_to_form(item_attr.doctype, item_attr.name)

	existing_values = [row.attribute_value for row in item_attr.item_attribute_values]
	existing_abbreviations = [row.abbr for row in item_attr.item_attribute_values]

	if attribute_value in existing_values:
		frappe.throw(_('Value "{}" exists already in Item Attribute {}.').format(attribute_value, item_attr_link))
	elif abbr in existing_abbreviations:
		frappe.throw(_('Abbreviation "{}" exists already in Item Attribute {}.').format(abbr, item_attr_link))
	else:
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
