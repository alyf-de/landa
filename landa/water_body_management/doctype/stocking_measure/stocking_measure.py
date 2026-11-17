# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from base64 import b64encode
from math import cos, log, pi, radians, tan

import frappe
import requests
from frappe import _

from landa.water_body_management.stocking_controller import StockingController

# Small map of each Stocking Site in the print format "Besatz"
TILE_SIZE = 256
MAP_ZOOM = 15
MAP_WIDTH = 240
MAP_HEIGHT = 160
MAP_TILE_CACHE_SECONDS = 7 * 24 * 60 * 60
# After a failed tile request, print without maps for a while instead of waiting for each site
MAP_TILES_UNAVAILABLE_CACHE_KEY = "landa_map_tiles_unavailable"
MAP_TILES_RETRY_SECONDS = 60


class StockingMeasure(StockingController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.water_body_management.doctype.stocking_measure_site.stocking_measure_site import (
			StockingMeasureSite,
		)

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
		stocking_sites: DF.TableMultiSelect[StockingMeasureSite]
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
		self.validate_stocking_sites()

	def validate_stocking_sites(self):
		for row in self.stocking_sites:
			site_title, site_water_body = frappe.db.get_value(
				"Stocking Site", row.stocking_site, ["title", "water_body"]
			)
			if site_water_body != self.water_body:
				frappe.throw(
					_("Stocking Site {0} must belong to the selected Water Body.").format(site_title)
				)

			site_has_recommendations = frappe.db.exists(
				"Fish Species And Type",
				{"parent": row.stocking_site, "parenttype": "Stocking Site"},
			)
			if not site_has_recommendations:
				continue

			if not frappe.db.exists(
				"Fish Species And Type",
				{
					"parent": row.stocking_site,
					"parenttype": "Stocking Site",
					"fish_species": self.fish_species,
				},
			):
				frappe.msgprint(
					_(
						"The selected Fish Species is not among the recommendations for Stocking Site {0}."
					).format(site_title),
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

	def get_stocking_site_details(self) -> list[dict]:
		"""Return title, description and coordinates of each Stocking Site, for printing."""
		details = []
		for row in self.stocking_sites:
			site = frappe.db.get_value(
				"Stocking Site",
				row.stocking_site,
				["title", "description", "longitude", "latitude"],
				as_dict=True,
			)
			has_coordinates = bool(site.longitude and site.latitude)
			site.map_tiles = get_map_tiles(site.longitude, site.latitude) if has_coordinates else []
			details.append(site)
		return details


def get_map_tiles(longitude: float, latitude: float) -> list[dict]:
	"""Return the OpenStreetMap tiles around a point, positioned to center it in the print map.

	The print format places each tile at `left`/`top` (px) inside a box of
	`MAP_WIDTH` x `MAP_HEIGHT` px and draws the marker in the middle of the box.
	Each tile comes as a `data:` URL, so the browser preview and the PDF need
	no access to the tile server. Returns no tiles if the tile server fails.
	"""
	if frappe.cache.get_value(MAP_TILES_UNAVAILABLE_CACHE_KEY, expires=True):
		return []

	world_size = TILE_SIZE * 2**MAP_ZOOM
	latitude_radians = radians(latitude)
	point_x = (longitude + 180) / 360 * world_size
	point_y = (1 - log(tan(latitude_radians) + 1 / cos(latitude_radians)) / pi) / 2 * world_size
	center_tile_x = int(point_x // TILE_SIZE)
	center_tile_y = int(point_y // TILE_SIZE)

	tiles = []
	for tile_y in range(center_tile_y - 1, center_tile_y + 2):
		for tile_x in range(center_tile_x - 1, center_tile_x + 2):
			left = round(MAP_WIDTH / 2 + tile_x * TILE_SIZE - point_x)
			top = round(MAP_HEIGHT / 2 + tile_y * TILE_SIZE - point_y)
			is_visible = -TILE_SIZE < left < MAP_WIDTH and -TILE_SIZE < top < MAP_HEIGHT
			if not is_visible:
				continue

			try:
				url = get_map_tile_data_url(tile_x, tile_y)
			except requests.RequestException:
				frappe.cache.set_value(
					MAP_TILES_UNAVAILABLE_CACHE_KEY, True, expires_in_sec=MAP_TILES_RETRY_SECONDS
				)
				return []

			tiles.append({"url": url, "left": left, "top": top})
	return tiles


def get_map_tile_data_url(tile_x: int, tile_y: int) -> str:
	"""Return an OpenStreetMap tile as `data:` URL, cached to respect the tile usage policy."""
	cache_key = f"landa_map_tile:{MAP_ZOOM}:{tile_x}:{tile_y}"
	data_url = frappe.cache.get_value(cache_key)
	if data_url:
		return data_url

	response = requests.get(
		f"https://tile.openstreetmap.org/{MAP_ZOOM}/{tile_x}/{tile_y}.png",
		headers={"User-Agent": f"LANDA (+{frappe.utils.get_url('/contact')})"},
		timeout=10,
	)
	response.raise_for_status()
	data_url = f"data:image/png;base64,{b64encode(response.content).decode()}"
	frappe.cache.set_value(cache_key, data_url, expires_in_sec=MAP_TILE_CACHE_SECONDS)
	return data_url


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def stocking_site_query(
	doctype: str, txt: str, searchfield: str, start: int, page_len: int, filters: dict
) -> list[tuple]:
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


@frappe.whitelist(methods=["POST"])
def create_stocking_targets(stocking_measure_names: str | list[str], year: str | int) -> None:
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
