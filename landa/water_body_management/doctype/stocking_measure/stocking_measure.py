# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from landa.water_body_management.stocking_controller import StockingController


class StockingMeasure(StockingController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_information: DF.SmallText | None
		company_of_supplier: DF.Data | None
		date: DF.Date
		fish_species: DF.Link
		fish_type_for_stocking: DF.Link
		fishing_area: DF.Link | None
		full_name_of_supplier: DF.Data | None
		organization: DF.Link
		quantity: DF.Float
		quantity_per_water_body_size: DF.Float
		status: DF.Literal["In Progress", "Completed"]
		stocking_site: DF.Link | None
		stocking_target: DF.Link | None
		supplier: DF.Link | None
		unit_of_quantity_per_water_body_size: DF.Data | None
		unit_of_weight_per_water_body_size: DF.Data | None
		water_body: DF.Link
		water_body_size: DF.Float
		water_body_size_unit: DF.Data | None
		water_body_title: DF.Data | None
		weight: DF.Float
		weight_per_water_body_size: DF.Float
		year: DF.Int

	# end: auto-generated types
	def validate(self):
		super().validate()
		self.validate_stocking_site()

	def validate_stocking_site(self):
		if not self.stocking_site:
			return

		if frappe.db.get_value("Stocking Site", self.stocking_site, "water_body") != self.water_body:
			frappe.throw(_("Stocking Site must belong to the selected Water Body."))

	def on_change(self):
		self.update_stocking_target()

	def after_delete(self):
		self.update_stocking_target()

	def update_stocking_target(self):
		if not self.stocking_target:
			return

		# saving a Stocking Target triggers validation, including a status update
		frappe.get_doc("Stocking Target", self.stocking_target).save()


@frappe.whitelist()
def create_stocking_targets(stocking_measure_names, year):
	import json

	if isinstance(stocking_measure_names, str):
		stocking_measure_names = json.loads(stocking_measure_names)

	stocking_measures = frappe.get_all(
		"Stocking Measure",
		filters={"name": ["in", stocking_measure_names]},
		fields=[
			"name",
			"fish_species",
			"fish_type_for_stocking",
			"organization",
			"water_body",
			"weight",
			"quantity",
		],
	)

	stocking_targets = {}

	for stocking_measure in stocking_measures:
		primary_key = (
			stocking_measure["fish_species"],
			stocking_measure["fish_type_for_stocking"],
			stocking_measure["water_body"],
		)

		if primary_key not in stocking_targets:
			stocking_targets[primary_key] = {
				"year": int(year),
				"organization": stocking_measure["organization"],
				"water_body": stocking_measure["water_body"],
				"fish_species": stocking_measure["fish_species"],
				"fish_type_for_stocking": stocking_measure["fish_type_for_stocking"],
				"weight": 0,
				"quantity": 0,
			}

		stocking_targets[primary_key]["weight"] += stocking_measure["weight"]
		stocking_targets[primary_key]["quantity"] += stocking_measure["quantity"]

	for stocking_target in list(stocking_targets.values()):
		doc = frappe.new_doc("Stocking Target")
		doc.update(stocking_target)
		doc.save()
