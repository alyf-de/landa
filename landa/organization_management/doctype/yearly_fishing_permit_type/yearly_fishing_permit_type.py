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
	item_attribute_values = [(row.attribute_value, row.abbr) for row in item_attr.item_attribute_values]

	existing_pairs = [row for row in item_attribute_values if row == (attribute_value, abbr)]
	if existing_pairs:
		# Item attribute exists already, as intended
		return

	existing_values = [row[0] for row in item_attribute_values]
	existing_abbreviations = [row[1] for row in item_attribute_values]

	if attribute_value in existing_values:
		# Attribute value exists, but with a different abbreviation
		frappe.throw(_('Value "{}" exists already in Item Attribute {}.').format(attribute_value, item_attr_link))

	if abbr in existing_abbreviations:
		# Abbreviation exists, but with a different attribute value
		frappe.throw(_('Abbreviation "{}" exists already in Item Attribute {}.').format(abbr, item_attr_link))

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
