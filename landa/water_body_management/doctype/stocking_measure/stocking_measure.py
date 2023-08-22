# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe

from landa.water_body_management.stocking_controller import StockingController


class StockingMeasure(StockingController):
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