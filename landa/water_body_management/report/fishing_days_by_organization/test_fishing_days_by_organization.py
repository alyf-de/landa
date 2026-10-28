from unittest.mock import patch

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests.utils import FrappeTestCase

from landa.water_body_management.report.fishing_days_by_organization.fishing_days_by_organization import (
	get_data,
)

test_dependencies = ["Catch Log Entry"]

REPORT_MODULE = "landa.water_body_management.report.fishing_days_by_organization.fishing_days_by_organization"
REGIONAL_ROLE = "LANDA Regional Organization Management"
STATE_ROLE = "LANDA State Organization Employee"
FILTERS = {"water_body": "A01-001", "from_year": 2023, "to_year": 2023}


class TestFishingDaysByOrganization(FrappeTestCase):
	def test_groups_fishing_days_and_limits_regional_organization(self):
		frappe.db.delete("Catch Log Entry")
		create_catch_log_entry("REG-001", 4)
		create_catch_log_entry("REG-001", 8)
		create_catch_log_entry("REG-002-01", 3)

		data = run_report(FILTERS, "REG", REGIONAL_ROLE)
		self.assertEqual(
			[(row.organization, row.fishing_days) for row in data],
			[("REG-001", 12), ("REG-002-01", 3)],
		)

		self.assertEqual(run_report(FILTERS, "OTHER", REGIONAL_ROLE), [])

		data = run_report(FILTERS, "OTHER", STATE_ROLE)
		self.assertEqual(
			{row.organization: row.fishing_days for row in data},
			{"REG-001": 12, "REG-002-01": 3},
		)

	def test_regional_organization_does_not_see_other_clubs_on_its_water_body(self):
		frappe.db.delete("Catch Log Entry")
		entry = create_catch_log_entry("REG-001", 4)
		# Simulate a club of region REG fishing on a water body of region OTHER
		frappe.db.set_value("Catch Log Entry", entry.name, "regional_organization", "OTHER")

		self.assertEqual(run_report(FILTERS, "OTHER", REGIONAL_ROLE), [])

	def test_organization_filter_includes_local_groups(self):
		frappe.db.delete("Catch Log Entry")
		create_catch_log_entry("REG-001", 4)
		create_catch_log_entry("REG-002-01", 3)

		data = run_report({**FILTERS, "organization": "REG-002"}, "REG", REGIONAL_ROLE)
		self.assertEqual(
			[(row.organization, row.fishing_days) for row in data],
			[("REG-002-01", 3)],
		)

	def test_renamed_organization_stays_in_one_row(self):
		frappe.db.delete("Catch Log Entry")
		old_entry = create_catch_log_entry("REG-001", 4)
		create_catch_log_entry("REG-001", 8)
		# Simulate an entry created before the organization was renamed
		frappe.db.set_value("Catch Log Entry", old_entry.name, "organization_name", "Old Name")

		data = run_report(FILTERS, "OTHER", STATE_ROLE)

		current_name = frappe.db.get_value("Organization", "REG-001", "organization_name")
		self.assertEqual(
			[(row.organization, row.organization_name, row.fishing_days) for row in data],
			[("REG-001", current_name, 12)],
		)


def run_report(filters, regional_organization, role):
	with patch(
		f"{REPORT_MODULE}.get_current_member_data",
		return_value=frappe._dict(regional_organization=regional_organization),
	), patch(
		f"{REPORT_MODULE}.get_user_roles",
		return_value={role},
	):
		return get_data(filters)


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
	return entry
