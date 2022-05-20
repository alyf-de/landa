# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import get_link_to_form

from landa.water_body_management.stocking_controller import StockingController


class StockingTarget(StockingController):
	def validate(self):
		super(StockingTarget, self).validate()
		self.validate_is_unique()

	def validate_is_unique(self):
		existing_stocking_target = frappe.db.get_value(
			self.doctype,
			{
				"year": self.year,
				"water_body": self.water_body,
				"fish_species": self.fish_species,
				"fish_type_for_stocking": self.fish_type_for_stocking,
			},
		)
		if existing_stocking_target and existing_stocking_target != self.name:
			frappe.throw(
				_("Please update the existing record: {0}").format(
					get_link_to_form(self.doctype, existing_stocking_target)
				)
			)


def copy_to_next_year() -> None:
	"""Copy all Stocking targets from the current year to the next year.

	Skip disabled Water Bodies, unset disabled suppliers (External Contact)."""
	from datetime import date

	doctype = "Stocking Target"
	current_year = date.today().year

	for old_target in frappe.get_all(
		doctype,
		filters={"year": str(current_year)},
		pluck="name",
	):
		old_doc = frappe.get_doc(doctype, old_target)
		if not frappe.db.get_value("Water Body", old_doc.water_body, "is_active"):
			continue

		new_doc = frappe.copy_doc(old_doc)
		new_doc.year = str(current_year + 1)
		if frappe.db.get_value("External Contact", old_doc.supplier, "disabled"):
			new_doc.supplier = None

		new_doc.save()


@frappe.whitelist()
def create_stocking_measure(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.validate()

	return get_mapped_doc(
		"Stocking Target",
		source_name,
		{
			"Stocking Target": {
				"doctype": "Stocking Measure",
				"field_map": {
					# [field name in Stocking Target]: [field name in Stocking Measure]
					"name": "stocking_target",
				},
			}
		},
		target_doc,
		set_missing_values,
		ignore_permissions=False,
	)
