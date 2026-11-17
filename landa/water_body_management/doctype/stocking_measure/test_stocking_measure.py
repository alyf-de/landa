# Copyright (c) 2022, Real Experts GmbH and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestStockingMeasure(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		state_organizations = frappe.get_all(
			"Organization", filters={"parent_organization": ("is", "not set")}, pluck="name"
		)
		cls.organization = frappe.db.get_value(
			"Organization", {"parent_organization": ("in", state_organizations)}
		)
		fishing_area = frappe.get_doc(
			{
				"doctype": "Fishing Area",
				"area_code": "TEST-BM",
				"area_name": "Test Stocking Measure",
				"organization": cls.organization,
			}
		).insert()
		cls.water_body = make_water_body(fishing_area.name, "1")
		cls.other_water_body = make_water_body(fishing_area.name, "2")
		cls.fish_species = frappe.get_doc({"doctype": "Fish Species", "title": "Test Fish"}).insert().name
		cls.fish_type = (
			frappe.get_doc({"doctype": "Fish Type For Stocking", "title": "Test Fish Type"}).insert().name
		)

	def test_multiple_stocking_sites(self):
		sites = [make_stocking_site(self.water_body, title) for title in ("North Shore", "South Shore")]

		measure = self.make_stocking_measure(sites)

		measure.reload()
		self.assertEqual([row.stocking_site for row in measure.stocking_sites], sites)

	def test_stocking_site_of_other_water_body(self):
		sites = [
			make_stocking_site(self.water_body, "Own Shore"),
			make_stocking_site(self.other_water_body, "Foreign Shore"),
		]

		self.assertRaises(frappe.ValidationError, self.make_stocking_measure, sites)

	def make_stocking_measure(self, stocking_sites: list[str]):
		return frappe.get_doc(
			{
				"doctype": "Stocking Measure",
				"date": "2026-04-01",
				"year": 2026,
				"organization": self.organization,
				"water_body": self.water_body,
				"fish_species": self.fish_species,
				"fish_type_for_stocking": self.fish_type,
				"weight": 10,
				"stocking_sites": [{"stocking_site": site} for site in stocking_sites],
			}
		).insert()


def make_water_body(fishing_area: str, number: str) -> str:
	water_body = frappe.get_doc(
		{
			"doctype": "Water Body",
			"title": f"Test Water Body {number}",
			"number": number,
			"fishing_area": fishing_area,
			"status": "Allgemeines Angelgewässer",
		}
	)
	water_body.flags.skip_cache_rebuild = True
	return water_body.insert().name


def make_stocking_site(water_body: str, title: str) -> str:
	return (
		frappe.get_doc({"doctype": "Stocking Site", "water_body": water_body, "title": title}).insert().name
	)
