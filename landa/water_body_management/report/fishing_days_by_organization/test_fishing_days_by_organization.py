from unittest.mock import patch

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests.utils import FrappeTestCase

from landa.water_body_management.report.fishing_days_by_organization.fishing_days_by_organization import (
	get_data,
)

test_dependencies = ["Catch Log Entry"]


class TestFishingDaysByOrganization(FrappeTestCase):
	def test_groups_fishing_days_by_organization_and_limits_regional_organization(self):
		frappe.db.delete("Catch Log Entry")
		create_catch_log_entry(4)
		create_catch_log_entry(8)

		filters = {"water_body": "A01-001", "from_year": 2023, "to_year": 2023}
		with patch(
			"landa.water_body_management.report.fishing_days_by_organization.fishing_days_by_organization.get_current_member_data",
			return_value=frappe._dict(regional_organization="REG"),
		):
			data = get_data(filters)

		self.assertEqual(len(data), 1)
		self.assertEqual(data[0].organization, "REG-001")
		self.assertEqual(data[0].fishing_days, 12)

		with patch(
			"landa.water_body_management.report.fishing_days_by_organization.fishing_days_by_organization.get_current_member_data",
			return_value=frappe._dict(regional_organization="OTHER"),
		):
			self.assertEqual(get_data(filters), [])


def create_catch_log_entry(fishing_days):
	entry = frappe.get_doc(
		{
			"doctype": "Catch Log Entry",
			"water_body": "A01-001",
			"year": 2023,
			"fishing_days": fishing_days,
			"organization": "REG-001",
			"origin_of_catch_log_entry": "Verein",
			"workflow_state": "In Progress",
		}
	)
	entry.save()
	apply_workflow(entry, "File this record")
	apply_workflow(entry, "Approve")
