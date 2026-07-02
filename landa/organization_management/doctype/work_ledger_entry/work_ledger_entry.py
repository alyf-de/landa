# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils.data import now_datetime


class WorkLedgerEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		date: DF.Date
		hours_change: DF.Float
		is_system_generated: DF.Check
		member: DF.Link
		member_name: DF.Data | None
		organization: DF.Link
		organization_name: DF.Data | None
		work_assignment: DF.Link | None
	# end: auto-generated types


def create_yearly_negative_entries():
	"""Create negative Work Ledger Entries for all members based on expected work hours per year."""

	entry_date = f"{now_datetime().year}-01-01"
	org = frappe.qb.DocType("Organization")
	member = frappe.qb.DocType("LANDA Member")
	ledger_entry = frappe.qb.DocType("Work Ledger Entry")

	query = (
		frappe.qb.from_(org)
		.join(member)
		.on(member.organization == org.name)
		.left_join(ledger_entry)
		.on(
			(ledger_entry.member == member.name)
			& (ledger_entry.organization == org.name)
			& (ledger_entry.date == entry_date)
			& (ledger_entry.is_system_generated == 1)
		)
		.select(
			member.name.as_("member"),
			org.name.as_("organization"),
			org.expected_work_hours_per_year,
		)
		.where(org.expected_work_hours_per_year > 0)
		.where(ledger_entry.name.isnull())
	)

	for row in query.run(as_dict=True):
		entry = frappe.new_doc("Work Ledger Entry")
		entry.member = row.member
		entry.organization = row.organization
		entry.date = entry_date
		entry.hours_change = -row.expected_work_hours_per_year
		entry.is_system_generated = 1
		entry.insert(ignore_permissions=True)


def create_expected_hours_adjustment_entries(organization: str, hours_change: float):
	"""
	Create one Work Ledger Entry per member of the organization for the given hours change.
	Its called when Organization.expected_work_hours_per_year is updated.
	"""

	if hours_change == 0:
		return

	members = frappe.get_list(
		"LANDA Member",
		filters={"organization": organization},
		fields=["name"],
	)
	for m in members:
		entry = frappe.new_doc("Work Ledger Entry")
		entry.organization = organization
		entry.member = m.name
		entry.date = getdate()
		entry.hours_change = hours_change
		entry.is_system_generated = 1
		entry.insert()
