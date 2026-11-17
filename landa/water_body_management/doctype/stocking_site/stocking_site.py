# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import json
from collections.abc import Sequence
from math import cos, hypot, pi
from typing import Any, TypeAlias

import frappe
from frappe.model.document import Document
from frappe.utils import flt

Coordinate: TypeAlias = Sequence[float]
Ring: TypeAlias = Sequence[Coordinate]
Line: TypeAlias = Sequence[Coordinate]
Polygon: TypeAlias = Sequence[Ring]
GeoJSON: TypeAlias = dict[str, Any]
WATER_BODY_MARGIN_METERS = 500
COORDINATE_PRECISION = 6  # Same as the precision of the fields `latitude` and `longitude`


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
		latitude: DF.Float
		location: DF.Geolocation | None
		longitude: DF.Float
		title: DF.Data
		water_body: DF.Link
	# end: auto-generated types

	def validate(self) -> None:
		self.sync_location()
		self.validate_location()

	def sync_location(self) -> None:
		"""Keep the marker and the coordinates in sync.

		The coordinates are read-only in the form, so they only change through
		Data Import or the API. Then they replace the marker. Otherwise they
		follow the marker.
		"""
		if self.coordinates_changed():
			self.location = make_location(self.longitude, self.latitude)
		else:
			longitude, latitude = get_location_point(self.location) or (0, 0)
			self.longitude = flt(longitude, COORDINATE_PRECISION)
			self.latitude = flt(latitude, COORDINATE_PRECISION)

	def coordinates_changed(self) -> bool:
		previous = self.get_doc_before_save()
		if not previous:
			return bool(flt(self.latitude) or flt(self.longitude))

		return (flt(self.latitude), flt(self.longitude)) != (previous.latitude, previous.longitude)

	def validate_location(self) -> None:
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


def make_location(longitude: float, latitude: float) -> str | None:
	"""Return a GeoJSON marker at the coordinates, or None if both are empty (zero)."""
	longitude, latitude = flt(longitude), flt(latitude)
	if not longitude and not latitude:
		return None
	if not longitude or not latitude:
		frappe.throw(frappe._("Please set both Latitude and Longitude."))

	return json.dumps(
		{
			"type": "FeatureCollection",
			"features": [
				{
					"type": "Feature",
					"properties": {},
					"geometry": {"type": "Point", "coordinates": [longitude, latitude]},
				}
			],
		}
	)


def point_near_water_body(point: Coordinate, geojson: GeoJSON) -> bool:
	"""Return whether a point is within the allowed margin of the Water Body."""
	for feature in geojson.get("features", []):
		geometry = feature.get("geometry", {})
		geometry_type = geometry.get("type")
		coordinates = geometry.get("coordinates")
		if geometry_type == "Polygon" and point_near_polygon(point, coordinates):
			return True
		if geometry_type == "MultiPolygon" and any(
			point_near_polygon(point, polygon) for polygon in coordinates
		):
			return True
		if geometry_type == "LineString" and point_near_line(point, coordinates):
			return True
		if geometry_type == "MultiLineString" and any(point_near_line(point, line) for line in coordinates):
			return True
	return False


def point_near_polygon(point: Coordinate, rings: Polygon) -> bool:
	"""Return whether a point is within the allowed margin of a polygon."""
	return point_in_polygon(point, rings) or any(
		distance_to_segment(point, coordinate, ring[(index + 1) % len(ring)]) <= WATER_BODY_MARGIN_METERS
		for ring in rings
		for index, coordinate in enumerate(ring)
	)


def point_near_line(point: Coordinate, line: Line) -> bool:
	"""Return whether a point is within the allowed margin of a line."""
	return any(
		distance_to_segment(point, line[index], line[index + 1]) <= WATER_BODY_MARGIN_METERS
		for index in range(len(line) - 1)
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
