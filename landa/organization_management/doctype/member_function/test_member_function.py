# Copyright (c) 2021, Real Experts GmbH and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from landa.organization_management.doctype.member_function.member_function import (
	update_member_function_status,
)

ROLE = "LANDA Local Organization Management"


class TestMemberFunction(FrappeTestCase):
	test_dependencies = ["Organization"]

	def setUp(self):
		self.organization = frappe.get_all("Organization", filters={"is_group": 0}, limit=1, pluck="name")[0]
		self.category = make_category("Test Function", only_one_per_organization=0)
		self.unique_category = make_category("Test Unique Function", only_one_per_organization=1)

	def tearDown(self):
		frappe.db.rollback()

	def make_member(self, last_name: str):
		member = frappe.get_doc(
			{"doctype": "LANDA Member", "organization": self.organization, "last_name": last_name}
		).insert()
		frappe.get_doc(
			{
				"doctype": "User",
				"email": f"{frappe.scrub(last_name)}@example.com",
				"first_name": last_name,
				"landa_member": member.name,
				"send_welcome_email": 0,
			}
		).insert()
		return member.name

	def make_member_function(self, member: str, category: str, start_date: str, end_date: str | None = None):
		return frappe.get_doc(
			{
				"doctype": "Member Function",
				"member": member,
				"member_function_category": category,
				"start_date": start_date,
				"end_date": end_date,
			}
		).insert()

	def make_due_planned_member_function(self, member: str, category: str):
		"""Simulate a Member Function that was saved as "Planned" and whose start date has arrived."""
		doc = self.make_member_function(member, category, add_days(today(), 1))
		doc.db_set("start_date", today())
		return doc.name

	def test_activates_due_planned_member_function(self):
		member = self.make_member("Planned Due")
		user = frappe.db.get_value("User", {"landa_member": member})
		member_function = self.make_due_planned_member_function(member, self.category)
		self.assertNotIn(ROLE, frappe.get_roles(user))

		update_member_function_status()

		self.assertEqual(frappe.db.get_value("Member Function", member_function, "status"), "Active")
		self.assertIn(ROLE, frappe.get_roles(user))

	def test_keeps_future_member_function_planned(self):
		member = self.make_member("Planned Future")
		member_function = self.make_member_function(member, self.category, add_days(today(), 1))

		update_member_function_status()

		self.assertEqual(frappe.db.get_value("Member Function", member_function.name, "status"), "Planned")

	def test_conflict_does_not_block_other_activations(self):
		holder = self.make_member("Unique Holder")
		self.make_member_function(holder, self.unique_category, add_days(today(), -10))
		conflicting = self.make_due_planned_member_function(
			self.make_member("Unique Conflict"), self.unique_category
		)
		other = self.make_due_planned_member_function(self.make_member("Other Planned"), self.category)

		update_member_function_status()

		self.assertEqual(frappe.db.get_value("Member Function", conflicting, "status"), "Planned")
		self.assertEqual(frappe.db.get_value("Member Function", other, "status"), "Active")

	def test_successor_is_activated_after_predecessor_expires(self):
		predecessor = self.make_member_function(
			self.make_member("Predecessor"), self.unique_category, add_days(today(), -10)
		)
		# The end date has passed, but the daily job has not set the status to "Inactive" yet.
		predecessor.db_set("end_date", add_days(today(), -1))
		successor = self.make_due_planned_member_function(self.make_member("Successor"), self.unique_category)

		update_member_function_status()

		self.assertEqual(frappe.db.get_value("Member Function", predecessor.name, "status"), "Inactive")
		self.assertEqual(frappe.db.get_value("Member Function", successor, "status"), "Active")


def make_category(name: str, only_one_per_organization: int) -> str:
	if not frappe.db.exists("Member Function Category", name):
		frappe.get_doc(
			{
				"doctype": "Member Function Category",
				"name": name,
				"access_level": "Local Group",
				"only_one_per_organization": only_one_per_organization,
				"roles": [{"role": ROLE}],
			}
		).insert()
	return name
