# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
from frappe.tests.utils import FrappeTestCase


class TestOrganization(FrappeTestCase):
	def setUp(self) -> None:
		test_records = frappe.get_test_records("Organization")
		for record in test_records:
			frappe.get_doc(record).insert()

	def test_naming(self):
		orgs = frappe.get_all("Organization", pluck="name")

		self.assertIn("ST", orgs)
		self.assertIn("REG", orgs)
		self.assertIn("REG-001", orgs)
		self.assertIn("REG-002", orgs)
		self.assertIn("REG-002-01", orgs)
