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
