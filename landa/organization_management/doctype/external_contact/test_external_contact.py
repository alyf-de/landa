# Copyright (c) 2022, Real Experts GmbH and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestExternalContact(FrappeTestCase):
	def test_autoname(self):
		contacts = frappe.get_all("External Contact", pluck="name")
		self.assertIn("EXT-REG-0001", contacts)
		self.assertIn("EXT-REG-0002", contacts)

	def test_full_name(self):
		self.assertTrue(frappe.db.exists("External Contact", {"full_name": "Jane Doe"}))

	def test_requires_full_name_or_organization_name(self):
		doc = frappe.new_doc("External Contact")
		doc.organization = "REG"
		doc.before_validate()
		self.assertRaises(frappe.ValidationError, doc.validate)

		doc.first_name = "Jane"
		doc.before_validate()
		doc.validate()
		self.assertEqual(doc.full_name, "Jane")

		org_only = frappe.new_doc("External Contact")
		org_only.organization = "REG"
		org_only.external_organization_name = "Acme"
		org_only.before_validate()
		org_only.validate()
