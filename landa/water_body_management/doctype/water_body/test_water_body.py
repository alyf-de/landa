# Copyright (c) 2021, Real Experts GmbH and Contributors
# See license.txt

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from landa.water_body_management.doctype.stocking_measure.test_stocking_measure import (
	make_stocking_site,
	make_water_body,
)

MARKER = {
	"type": "FeatureCollection",
	"features": [
		{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [13.95, 50.99]}}
	],
}
EMPTY_MARKER = {"type": "FeatureCollection", "features": []}


class TestWaterBody(FrappeTestCase):
	def test_has_stocking_site_map(self):
		state_organizations = frappe.get_all(
			"Organization", filters={"parent_organization": ("is", "not set")}, pluck="name"
		)
		organization = frappe.db.get_value(
			"Organization", {"parent_organization": ("in", state_organizations)}
		)
		fishing_area = frappe.get_doc(
			{
				"doctype": "Fishing Area",
				"area_code": "TEST-WB",
				"area_name": "Test Water Body",
				"organization": organization,
			}
		).insert()
		water_body = frappe.get_doc("Water Body", make_water_body(fishing_area.name, "1"))
		self.assertFalse(water_body.has_stocking_site_map())

		site = make_stocking_site(water_body.name, "Meadow")
		self.assertFalse(water_body.has_stocking_site_map(), "Site without marker")

		# This remains after deleting the marker in the form
		frappe.db.set_value("Stocking Site", site, "location", json.dumps(EMPTY_MARKER))
		self.assertFalse(water_body.has_stocking_site_map(), "Site with deleted marker")

		# Set the marker directly: the test Water Body has no boundary to validate against.
		frappe.db.set_value(
			"Stocking Site",
			site,
			{"location": frappe.as_json(MARKER), "longitude": 13.95, "latitude": 50.99},
		)
		self.assertTrue(water_body.has_stocking_site_map())

		with self.set_user("Guest"):
			self.assertFalse(water_body.has_stocking_site_map(), "No read permission")
