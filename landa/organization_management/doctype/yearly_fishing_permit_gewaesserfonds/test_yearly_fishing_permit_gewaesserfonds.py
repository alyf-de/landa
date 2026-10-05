# Copyright (c) 2026, ALYF GmbH and Contributors
# See license.txt

import json
from datetime import datetime

import frappe
from frappe.tests.utils import FrappeTestCase

from landa.organization_management.doctype.yearly_fishing_permit_gewaesserfonds.yearly_fishing_permit_gewaesserfonds import (
	bulk_create,
)
from landa.organization_management.report.current_member_data.current_member_data import execute


class TestYearlyFishingPermitGewaesserfonds(FrappeTestCase):
	test_dependencies = ["Organization"]

	def test_organization_comes_from_the_member(self):
		"""`organization` is fetched from the member, so a permit cannot land in another organization."""
		organizations = frappe.get_all("Organization", filters={"is_group": 0}, limit=2, pluck="name")
		member_organization, other_organization = organizations
		member = frappe.get_doc(
			{
				"doctype": "LANDA Member",
				"organization": member_organization,
				"last_name": "Gewaesserfonds",
			}
		).insert()

		permit = frappe.get_doc(
			{
				"doctype": "Yearly Fishing Permit Gewaesserfonds",
				"member": member.name,
				"organization": other_organization,
				"year": datetime.now().year,
				"association_or_state": "Berlin",
			}
		).insert()

		self.assertEqual(permit.organization, member_organization)

	def test_status_follows_year(self):
		organization = frappe.get_all("Organization", filters={"is_group": 0}, limit=1, pluck="name")[0]
		member = frappe.get_doc(
			{"doctype": "LANDA Member", "organization": organization, "last_name": "Gewaesserfonds"}
		).insert()
		this_year = datetime.now().year

		def make_permit(year, association_or_state):
			return frappe.get_doc(
				{
					"doctype": "Yearly Fishing Permit Gewaesserfonds",
					"member": member.name,
					"organization": organization,
					"year": year,
					"association_or_state": association_or_state,
				}
			).insert()

		self.assertEqual(make_permit(this_year - 1, "Berlin").status, "Inactive")
		self.assertEqual(make_permit(this_year, "LAVT").status, "Active")
		self.assertEqual(make_permit(this_year + 1, "VANT").status, "Planned")

	def test_bulk_create_skips_existing(self):
		organization = frappe.get_all("Organization", filters={"is_group": 0}, limit=1, pluck="name")[0]
		members = json.dumps(
			[
				frappe.get_doc({"doctype": "LANDA Member", "organization": organization, "last_name": name})
				.insert()
				.name
				for name in ("Bulk One", "Bulk Two")
			]
		)
		year = datetime.now().year

		self.assertEqual(bulk_create(year, "LAVT", members), {"num_created": 2, "num_skipped": 0})
		self.assertEqual(bulk_create(year, "LAVT", members), {"num_created": 0, "num_skipped": 2})

	def test_import_rejects_implausible_year(self):
		organization = frappe.get_all("Organization", filters={"is_group": 0}, limit=1, pluck="name")[0]
		member = frappe.get_doc(
			{"doctype": "LANDA Member", "organization": organization, "last_name": "Gewaesserfonds"}
		).insert()

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Member Data Import",
					"member": member.name,
					"organization": organization,
					"has_special_yearly_fishing_permit_3": 25,
				}
			).insert()

	def test_import_and_report_round_trip(self):
		"""`has_special_yearly_fishing_permit_3` is the Berlin permit, in both directions."""
		organization = frappe.get_all("Organization", filters={"is_group": 0}, limit=1, pluck="name")[0]
		year = datetime.now().year
		member = frappe.get_doc(
			{"doctype": "LANDA Member", "organization": organization, "last_name": "Gewaesserfonds"}
		).insert()
		# a second member without any permit, so that the report mixes years and blanks
		frappe.get_doc(
			{"doctype": "LANDA Member", "organization": organization, "last_name": "Kein Schein"}
		).insert()

		frappe.get_doc(
			{
				"doctype": "Member Data Import",
				"member": member.name,
				"organization": organization,
				"has_special_yearly_fishing_permit_3": year,
			}
		).insert()

		self.assertTrue(
			frappe.db.exists(
				"Yearly Fishing Permit Gewaesserfonds",
				{"member": member.name, "year": year, "association_or_state": "Berlin"},
			)
		)

		columns, data = execute({"organization": organization})
		fieldnames = [column["fieldname"] for column in columns]
		row = next(row for row in data if row[0] == member.name)

		berlin_year = row[fieldnames.index("has_special_yearly_fishing_permit_3")]
		self.assertEqual(berlin_year, year)
		# the blank of the other member must not turn this into "2026.0"
		self.assertEqual(str(berlin_year), str(year))
		self.assertEqual(row[fieldnames.index("has_special_yearly_fishing_permit_1")], "")
