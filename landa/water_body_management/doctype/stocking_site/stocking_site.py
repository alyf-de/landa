# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import json
from collections.abc import Sequence
from math import cos, hypot, pi
from typing import Any, TypeAlias

import frappe
from frappe.model.document import Document

Coordinate: TypeAlias = Sequence[float]
Ring: TypeAlias = Sequence[Coordinate]
Polygon: TypeAlias = Sequence[Ring]
GeoJSON: TypeAlias = dict[str, Any]
WATER_BODY_MARGIN_METERS = 500


class StockingSite(Document):
	"""A potential stocking location associated with a Water Body."""

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.water_body_management.doctype.fish_species_and_type.fish_species_and_type import (
			FishSpeciesAndType,
		)

		description: DF.SmallText | None
		disabled: DF.Check
		fish_species: DF.Table[FishSpeciesAndType]
		title: DF.Data
		water_body: DF.Link
	# end: auto-generated types

	def validate(self) -> None:
		"""Validate that the optional marker lies within the allowed area."""
		point = get_location_point(self.location)
		if not point:
			return

		water_body_location = frappe.db.get_value("Water Body", self.water_body, "location")
		if not water_body_location:
			frappe.throw(frappe._("The selected Water Body has no location boundary."))

		if not point_near_water_body(point, json.loads(water_body_location)):
			frappe.throw(
				frappe._("The location marker must be within {0} m of the Water Body.").format(
					WATER_BODY_MARGIN_METERS
				)
			)


@frappe.whitelist()
def get_water_body_map_data(water_body: str) -> dict[str, str | int | None]:
	"""Return the permitted Water Body geometry and marker margin."""
	return {
		"location": get_permitted_water_body_location(water_body),
		"margin_meters": WATER_BODY_MARGIN_METERS,
	}


@frappe.whitelist()
def is_point_near_water_body(water_body: str, longitude: float, latitude: float) -> bool:
	"""Return whether a point lies within the permitted Water Body area."""
	location = get_permitted_water_body_location(water_body)
	return bool(
		location
		and point_near_water_body(
			(float(longitude), float(latitude)),
			json.loads(location),
		)
	)


def get_permitted_water_body_location(water_body: str) -> str | None:
	"""Return a Water Body location after checking read permission."""
	water_body_doc = frappe.get_doc("Water Body", water_body)
	water_body_doc.check_permission("read")
	return water_body_doc.location


def get_location_point(location: str | None) -> Coordinate | None:
	"""Return the sole Point coordinates from a Stocking Site GeoJSON value."""
	if not location:
		return None

	try:
		geojson = json.loads(location)
		features = geojson["features"]
		if geojson.get("type") == "FeatureCollection" and not features:
			return None
		geometry = features[0]["geometry"]
		coordinates = geometry["coordinates"]
	except (json.JSONDecodeError, TypeError, KeyError, IndexError):
		frappe.throw(frappe._("At most one location marker is allowed."))

	if (
		geojson.get("type") != "FeatureCollection"
		or len(features) != 1
		or geometry.get("type") != "Point"
		or len(coordinates) < 2
	):
		frappe.throw(frappe._("At most one location marker is allowed."))

	return coordinates[:2]


def point_near_water_body(point: Coordinate, geojson: GeoJSON) -> bool:
	"""Return whether a point is within the allowed margin of the Water Body."""
	for feature in geojson.get("features", []):
		geometry = feature.get("geometry", {})
		if geometry.get("type") == "Polygon" and point_near_polygon(point, geometry["coordinates"]):
			return True
		if geometry.get("type") == "MultiPolygon" and any(
			point_near_polygon(point, polygon) for polygon in geometry["coordinates"]
		):
			return True
	return False


def point_near_polygon(point: Coordinate, rings: Polygon) -> bool:
	"""Return whether a point is within the allowed margin of a polygon."""
	return point_in_polygon(point, rings) or any(
		distance_to_segment(point, coordinate, ring[(index + 1) % len(ring)]) <= WATER_BODY_MARGIN_METERS
		for ring in rings
		for index, coordinate in enumerate(ring)
	)


def point_in_polygon(point: Coordinate, rings: Polygon) -> bool:
	"""Return whether a point is inside a polygon and outside its holes."""
	return point_in_ring(point, rings[0]) and not any(point_in_ring(point, ring) for ring in rings[1:])


def point_in_ring(point: Coordinate, ring: Ring) -> bool:
	"""Return whether a point is inside a linear ring using ray casting."""
	x, y = point
	inside = False
	j = len(ring) - 1
	for i, (xi, yi) in enumerate(ring):
		xj, yj = ring[j]
		if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
			inside = not inside
		j = i
	return inside


def distance_to_segment(point: Coordinate, start: Coordinate, end: Coordinate) -> float:
	"""Return the approximate distance in metres from a point to a segment."""
	earth_radius = 6371000
	latitude = point[1] * pi / 180

	def project(coordinate: Coordinate) -> tuple[float, float]:
		"""Project a coordinate to a local Cartesian plane around the point."""
		return (
			earth_radius * (coordinate[0] - point[0]) * pi / 180 * cos(latitude),
			earth_radius * (coordinate[1] - point[1]) * pi / 180,
		)

	start_x, start_y = project(start)
	end_x, end_y = project(end)
	length_squared = (end_x - start_x) ** 2 + (end_y - start_y) ** 2
	ratio = (
		max(
			0,
			min(
				1,
				(-start_x * (end_x - start_x) - start_y * (end_y - start_y)) / length_squared,
			),
		)
		if length_squared
		else 0
	)
	return hypot(
		start_x + ratio * (end_x - start_x),
		start_y + ratio * (end_y - start_y),
	)
