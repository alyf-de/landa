from unittest.mock import patch

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests.utils import FrappeTestCase

from landa.water_body_management.report.fishing_days_by_organization.fishing_days_by_organization import (
	get_data,
)

test_dependencies = ["Catch Log Entry"]


class TestFishingDaysByOrganization(FrappeTestCase):
	def test_groups_fishing_days_and_limits_regional_organization(self):
		frappe.db.delete("Catch Log Entry")
		create_catch_log_entry("REG-001", 4)
		create_catch_log_entry("REG-001", 8)
		create_catch_log_entry("REG-002-01", 3)

		filters = {"water_body": "A01-001", "from_year": 2023, "to_year": 2023}
		with patch(
			"landa.water_body_management.report.utils.get_current_member_data",
			return_value=frappe._dict(regional_organization="REG"),
		), patch(
			"landa.water_body_management.report.utils.get_user_roles",
			return_value={"LANDA Regional Organization Management"},
		):
			data = get_data(filters)

		self.assertEqual(
			{row.organization: row.fishing_days for row in data},
			{"REG-001": 12, "REG-002-01": 3},
		)

		with patch(
			"landa.water_body_management.report.utils.get_current_member_data",
			return_value=frappe._dict(regional_organization="OTHER"),
		), patch(
			"landa.water_body_management.report.utils.get_user_roles",
			return_value={"LANDA Regional Organization Management"},
		):
			self.assertEqual(get_data(filters), [])

		with patch(
			"landa.water_body_management.report.utils.get_current_member_data",
			return_value=frappe._dict(regional_organization="OTHER"),
		), patch(
			"landa.water_body_management.report.utils.get_user_roles",
			return_value={"LANDA State Organization Employee"},
		):
			data = get_data(filters)

		self.assertEqual(
			{row.organization: row.fishing_days for row in data},
			{"REG-001": 12, "REG-002-01": 3},
		)


def create_catch_log_entry(organization, fishing_days):
	entry = frappe.get_doc(
		{
			"doctype": "Catch Log Entry",
			"water_body": "A01-001",
			"year": 2023,
			"fishing_days": fishing_days,
			"organization": organization,
			"origin_of_catch_log_entry": "Verein",
			"workflow_state": "In Progress",
		}
	)
	entry.save()
	apply_workflow(entry, "File this record")
	apply_workflow(entry, "Approve")
