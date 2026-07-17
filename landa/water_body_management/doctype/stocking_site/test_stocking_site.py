# Copyright (c) 2026, ALYF GmbH and Contributors
# See license.txt

import json
from math import pi

import frappe
from frappe.tests.utils import FrappeTestCase

from landa.water_body_management.doctype.stocking_site.stocking_site import (
	WATER_BODY_MARGIN_METERS,
	distance_to_segment,
	get_location_point,
	point_in_polygon,
	point_in_ring,
	point_near_polygon,
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

	@staticmethod
	def longitude_for_distance(distance: float) -> float:
		return distance / EARTH_RADIUS_METERS * 180 / pi
