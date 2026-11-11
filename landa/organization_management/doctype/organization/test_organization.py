# Copyright (c) 2021, Real Experts GmbH and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from landa.organization_management.doctype.organization.organization import create_customer


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

	def test_customer_gets_price_list_of_company(self):
		company = frappe.db.get_value("Company", {"abbr": "REG"})
		price_list = frappe.get_doc(
			{
				"doctype": "Price List",
				"price_list_name": "Standard - REG",
				"currency": "EUR",
				"selling": 1,
				"company": company,
			}
		).insert()
		organization = frappe.get_doc(
			{
				"doctype": "Organization",
				"organization_name": "Local Organization with Price List",
				"parent_organization": "REG",
			}
		).insert()

		create_customer(organization.name, organization.organization_name)

		self.assertEqual(
			frappe.db.get_value("Customer", organization.name, "default_price_list"), price_list.name
		)
