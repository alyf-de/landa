# Copyright (c) 2026, ALYF GmbH and Contributors
# See license.txt

import json
from math import pi

import frappe
from frappe.tests.utils import FrappeTestCase

from landa.water_body_management.doctype.stocking_measure.test_stocking_measure import make_water_body
from landa.water_body_management.doctype.stocking_site.stocking_site import (
	WATER_BODY_MARGIN_METERS,
	distance_to_segment,
	get_location_point,
	make_location,
	point_in_polygon,
	point_in_ring,
	point_near_line,
	point_near_polygon,
	point_near_water_body,
)

EARTH_RADIUS_METERS = 6371000
OUTER_RING = [[-0.01, -0.01], [0.01, -0.01], [0.01, 0.01], [-0.01, 0.01], [-0.01, -0.01]]


class TestStockingSite(FrappeTestCase):
	def test_point_in_ring(self):
		self.assertTrue(point_in_ring([0, 0], OUTER_RING))
		self.assertFalse(point_in_ring([0.02, 0], OUTER_RING))

	def test_point_inside_polygon_hole(self):
		hole = [[-0.001, -0.001], [0.001, -0.001], [0.001, 0.001], [-0.001, 0.001], [-0.001, -0.001]]

		self.assertFalse(point_in_polygon([0, 0], [OUTER_RING, hole]))
		self.assertTrue(point_in_polygon([0.005, 0], [OUTER_RING, hole]))

	def test_distance_to_segment(self):
		longitude = self.longitude_for_distance(400)

		self.assertAlmostEqual(
			distance_to_segment([longitude, 0], [0, -0.01], [0, 0.01]),
			400,
			delta=0.01,
		)

	def test_point_within_and_beyond_margin(self):
		polygon = [[[0, -0.01], [0, 0.01], [-0.01, 0.01], [-0.01, -0.01], [0, -0.01]]]

		self.assertTrue(
			point_near_polygon(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS - 1), 0],
				polygon,
			)
		)
		self.assertFalse(
			point_near_polygon(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS + 1), 0],
				polygon,
			)
		)

	def test_point_near_line_within_and_beyond_margin(self):
		line = [[0, -0.01], [0, 0.01]]

		self.assertTrue(
			point_near_line(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS - 1), 0],
				line,
			)
		)
		self.assertFalse(
			point_near_line(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS + 1), 0],
				line,
			)
		)

	def test_point_near_water_body_line_string(self):
		geojson = {
			"type": "FeatureCollection",
			"features": [
				{
					"type": "Feature",
					"properties": {},
					"geometry": {
						"type": "LineString",
						"coordinates": [[0, -0.01], [0, 0.01]],
					},
				}
			],
		}

		self.assertTrue(
			point_near_water_body(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS - 1), 0],
				geojson,
			)
		)
		self.assertFalse(
			point_near_water_body(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS + 1), 0],
				geojson,
			)
		)

	def test_point_near_water_body_multi_line_string(self):
		# Match a point near the second line only, so the MultiLineString loop is exercised.
		geojson = {
			"type": "FeatureCollection",
			"features": [
				{
					"type": "Feature",
					"properties": {},
					"geometry": {
						"type": "MultiLineString",
						"coordinates": [
							[[1, -0.01], [1, 0.01]],
							[[0, -0.01], [0, 0.01]],
						],
					},
				}
			],
		}

		self.assertTrue(
			point_near_water_body(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS - 1), 0],
				geojson,
			)
		)
		self.assertFalse(
			point_near_water_body(
				[self.longitude_for_distance(WATER_BODY_MARGIN_METERS + 1), 0],
				geojson,
			)
		)

	def test_get_location_point(self):
		self.assertIsNone(get_location_point(None))
		self.assertIsNone(get_location_point(json.dumps({"type": "FeatureCollection", "features": []})))
		self.assertEqual(
			get_location_point(
				json.dumps(
					{
						"type": "FeatureCollection",
						"features": [
							{
								"type": "Feature",
								"properties": {},
								"geometry": {"type": "Point", "coordinates": [12, 51]},
							}
						],
					}
				)
			),
			[12, 51],
		)

	def test_get_location_point_rejects_malformed_geojson(self):
		invalid_locations = [
			"{",
			json.dumps({"type": "FeatureCollection", "features": [{}]}),
			json.dumps(
				{
					"type": "FeatureCollection",
					"features": [
						{
							"type": "Feature",
							"properties": {},
							"geometry": {"type": "Polygon", "coordinates": [OUTER_RING]},
						}
					],
				}
			),
		]

		for location in invalid_locations:
			with self.subTest(location=location), self.assertRaises(frappe.ValidationError):
				get_location_point(location)

	def test_sync_location_and_coordinates(self):
		site = frappe.get_doc(
			{
				"doctype": "Stocking Site",
				"water_body": make_water_body_with_boundary(),
				"title": "Imported",
				"longitude": "13.95",
				"latitude": "50.99",
			}
		).insert()
		self.assertEqual(get_location_point(site.location), [13.95, 50.99], "Import creates the marker")

		site.location = make_location(13.951234567, 50.991234567)
		site.save()
		self.assertEqual((site.longitude, site.latitude), (13.951235, 50.991235), "Marker sets coordinates")

		site.longitude, site.latitude = 13.952, 50.992
		site.save()
		self.assertEqual(get_location_point(site.location), [13.952, 50.992], "Import moves the marker")

		site.latitude = 0
		self.assertRaises(frappe.ValidationError, site.save)

		site.reload()
		site.longitude, site.latitude = 0, 0
		site.save()
		self.assertIsNone(site.location, "Import removes the marker")

	@staticmethod
	def longitude_for_distance(distance: float) -> float:
		return distance / EARTH_RADIUS_METERS * 180 / pi


def make_water_body_with_boundary() -> str:
	state_organizations = frappe.get_all(
		"Organization", filters={"parent_organization": ("is", "not set")}, pluck="name"
	)
	organization = frappe.db.get_value("Organization", {"parent_organization": ("in", state_organizations)})
	fishing_area = frappe.get_doc(
		{
			"doctype": "Fishing Area",
			"area_code": "TEST-SS",
			"area_name": "Test Stocking Site",
			"organization": organization,
		}
	).insert()
	water_body = make_water_body(fishing_area.name, "1")
	boundary = [[[13.94, 50.98], [13.96, 50.98], [13.96, 51.0], [13.94, 51.0], [13.94, 50.98]]]
	location = {
		"type": "FeatureCollection",
		"features": [
			{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": boundary}}
		],
	}
	frappe.db.set_value("Water Body", water_body, "location", json.dumps(location))
	return water_body
