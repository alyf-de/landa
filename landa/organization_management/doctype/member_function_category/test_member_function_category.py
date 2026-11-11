# Copyright (c) 2021, Real Experts GmbH and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

test_dependencies = ["Organization"]


class TestMemberFunctionCategory(FrappeTestCase):
	def test_access_level_with_member_administration(self):
		"""A category with member administration grants access at its access level."""
		category = make_category("Regional Organization", member_administration=1)
		member, user = make_member_with_user("REG-001")

		make_member_function(member, category)

		self.assertEqual(get_allowed_organizations(user), ["REG"])

	def test_access_level_without_member_administration(self):
		"""The access level of a category without member administration has no effect."""
		category = make_category("Regional Organization")
		member, user = make_member_with_user("REG-001")

		make_member_function(member, category)

		self.assertEqual(get_allowed_organizations(user), ["REG-001"])

	def test_planned_member_function_grants_no_access(self):
		"""A member function that starts in the future doesn't grant access yet."""
		regional_category = make_category("Regional Organization", member_administration=1)
		local_category = make_category("Local Group", member_administration=1)
		member, user = make_member_with_user("REG-001")

		make_member_function(member, regional_category, start_date=add_days(today(), 10))
		make_member_function(member, local_category)

		self.assertEqual(get_allowed_organizations(user), ["REG-001"])


def make_category(access_level, member_administration=0):
	return frappe.get_doc(
		{
			"doctype": "Member Function Category",
			"__newname": f"{access_level} {frappe.generate_hash(length=6)}",
			"access_level": access_level,
			"member_administration": member_administration,
		}
	).insert()


def make_member_with_user(organization):
	member = frappe.get_doc(
		{
			"doctype": "LANDA Member",
			"first_name": "Test",
			"last_name": "Member",
			"organization": organization,
		}
	).insert()
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": f"{frappe.generate_hash(length=8)}@example.com",
			"first_name": "Test",
			"landa_member": member.name,
		}
	).insert()
	return member, user


def make_member_function(member, category, start_date=None):
	return frappe.get_doc(
		{
			"doctype": "Member Function",
			"member": member.name,
			"member_function_category": category.name,
			"start_date": start_date,
		}
	).insert()


def get_allowed_organizations(user):
	return frappe.get_all("User Permission", {"user": user.name, "allow": "Organization"}, pluck="for_value")
