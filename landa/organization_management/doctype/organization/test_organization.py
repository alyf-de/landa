# Copyright (c) 2021, Real Experts GmbH and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestOrganization(FrappeTestCase):
	def test_autoname(self):
		orgs = frappe.get_all("Organization", pluck="name")

		self.assertIn("ST", orgs)
		self.assertIn("REG", orgs)
		self.assertIn("REG-001", orgs)
		self.assertIn("REG-002", orgs)
		self.assertIn("REG-002-01", orgs)

	def test_company_and_customer_exist(self):
		self.assertTrue(frappe.db.exists("Company", {"abbr": "REG"}))
		self.assertTrue(frappe.db.exists("Customer", "REG-001"))
		self.assertTrue(frappe.db.exists("Customer", "REG-002"))
