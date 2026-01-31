# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import now_datetime


class WorkLedgerEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		date: DF.Date
		hours_change: DF.Float
		member: DF.Link
		member_name: DF.Data | None
		organization: DF.Link
		organization_name: DF.Data | None
		work_assignment: DF.Link | None
	# end: auto-generated types
	pass


def create_yearly_negative_entries():
	"""Create negative Work Ledger Entries for all members based on expected work hours per year."""

	organizations = frappe.get_list(
		"Organization",
		filters={"expected_work_hours_per_year": [">", 0]},
		fields=["name", "expected_work_hours_per_year"],
	)

	if not organizations:
		return

	# Get all active members for each organization
	for org in organizations:
		members = frappe.get_list(
			"LANDA Member",
			filters={"organization": org.name},
			fields=["name"],
		)

		for member in members:
			ledger_entry = frappe.new_doc("Work Ledger Entry")
			ledger_entry.member = member.name
			ledger_entry.organization = org.name
			ledger_entry.date = f"{now_datetime().year}-01-01"
			ledger_entry.hours_change = -org.expected_work_hours_per_year
			ledger_entry.insert()
