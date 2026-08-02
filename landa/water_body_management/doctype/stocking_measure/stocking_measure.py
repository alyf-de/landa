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

		site_has_recommendations = frappe.db.exists(
			"Fish Species And Type",
			{"parent": self.stocking_site, "parenttype": "Stocking Site"},
		)
		if not site_has_recommendations:
			return

		if not frappe.db.exists(
			"Fish Species And Type",
			{
				"parent": self.stocking_site,
				"parenttype": "Stocking Site",
				"fish_species": self.fish_species,
			},
		):
			frappe.msgprint(
				_("The selected Fish Species is not among the recommendations for this Stocking Site."),
				indicator="orange",
				alert=True,
			)

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
@frappe.validate_and_sanitize_search_inputs
def stocking_site_query(doctype, txt, searchfield, start, page_len, filters):
	"""Stocking Sites for a Water Body, with recommended species/type matches first."""
	filters = frappe._dict(filters or {})
	if not filters.water_body:
		return []

	sites = frappe.get_list(
		"Stocking Site",
		filters={"water_body": filters.water_body},
		or_filters={
			"name": ("like", f"%{txt}%"),
			"title": ("like", f"%{txt}%"),
		},
		fields=["name", "title"],
		order_by="title",
	)
	if not sites:
		return []

	recommendations_by_site = {}
	for row in frappe.get_all(
		"Fish Species And Type",
		filters={
			"parenttype": "Stocking Site",
			"parent": ["in", [site.name for site in sites]],
		},
		fields=["parent", "fish_species", "fish_type_for_stocking"],
		order_by="idx",
	):
		recommendations_by_site.setdefault(row.parent, []).append(row)

	fish_species = filters.fish_species or ""
	fish_type = filters.fish_type_for_stocking or ""

	def match_rank(row):
		if row.fish_species != fish_species:
			return 2
		if row.fish_type_for_stocking == fish_type:
			return 0
		return 1

	def format_recommendation(row):
		species = frappe.bold(row.fish_species) if row.fish_species == fish_species else row.fish_species
		stocking_type = (
			frappe.bold(row.fish_type_for_stocking)
			if row.fish_type_for_stocking == fish_type
			else row.fish_type_for_stocking
		)
		if row.fish_species and row.fish_type_for_stocking:
			return f"{species} ({stocking_type})"
		return species or stocking_type or ""

	def site_match_rank(site_name):
		ranks = [match_rank(row) for row in recommendations_by_site.get(site_name, [])]
		return min(ranks) if ranks else 2

	sites = sorted(
		sites,
		key=lambda site: (site_match_rank(site.name), site.title or site.name),
	)[start : start + page_len]

	results = []
	for site in sites:
		recommendations = sorted(
			recommendations_by_site.get(site.name, []),
			key=lambda row: (match_rank(row), row.fish_species or "", row.fish_type_for_stocking or ""),
		)
		description = ", ".join(format_recommendation(row) for row in recommendations)
		results.append((site.name, site.title, description) if description else (site.name, site.title))

	return results


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
