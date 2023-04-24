# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import get_link_to_form


class YearlyFishingPermitType(Document):
	def validate(self):
		validate_item_attribute(self.item_attribute, self.title, self.name)

	def on_submit(self):
		add_attribute_value(self.item_attribute, self.title, self.name)


def validate_item_attribute(item_attribute_name, attribute_value, abbr):
	item_attr = frappe.get_doc("Item Attribute", item_attribute_name)
	item_attribute_values = rows_to_tuples(item_attr.item_attribute_values)

	if (attribute_value, abbr) in item_attribute_values:
		# Item attribute exists already, as intended
		return

	existing_values = [row[0] for row in item_attribute_values]
	existing_abbreviations = [row[1] for row in item_attribute_values]
	item_attr_link = get_link_to_form(item_attr.doctype, item_attr.name)

	if attribute_value in existing_values:
		# Attribute value exists, but with a different abbreviation
		frappe.throw(
			_('Value "{}" exists already in Item Attribute {}.').format(attribute_value, item_attr_link)
		)

	if abbr in existing_abbreviations:
		# Abbreviation exists, but with a different attribute value
		frappe.throw(
			_('Abbreviation "{}" exists already in Item Attribute {}.').format(abbr, item_attr_link)
		)


def rows_to_tuples(rows):
	return [(row.attribute_value, row.abbr) for row in rows]


def add_attribute_value(item_attribute_name, attribute_value, abbr):
	"""Add a row (attribute_value, abbr) to Item Attibute."""
	item_attr = frappe.get_doc("Item Attribute", item_attribute_name)
	item_attribute_values = rows_to_tuples(item_attr.item_attribute_values)
	if (attribute_value, abbr) in item_attribute_values:
		# Item attribute exists already, as intended
		return

	item_attr.append("item_attribute_values", {"attribute_value": attribute_value, "abbr": abbr})
	item_attr.save()
