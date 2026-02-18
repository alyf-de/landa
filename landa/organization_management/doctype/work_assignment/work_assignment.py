# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WorkAssignment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.organization_management.doctype.work_assignment_member.work_assignment_member import (
			WorkAssignmentMember,
		)

		amended_from: DF.Link | None
		date: DF.Date
		description: DF.SmallText | None
		location: DF.Data | None
		members: DF.Table[WorkAssignmentMember]
		organization: DF.Link
		organization_name: DF.Data | None
		planned_duration: DF.Float
		title: DF.Data
		water_body: DF.Link | None
		water_body_title: DF.Data | None
	# end: auto-generated types

	def on_submit(self):
		self.create_work_ledger_entry()

	def on_cancel(self):
		self.delete_work_ledger_entry()

	def create_work_ledger_entry(self):
		if not self.members:
			return
		for member in self.members:
			work_ledger_entry = frappe.new_doc("Work Ledger Entry")
			work_ledger_entry.member = member.member
			work_ledger_entry.organization = self.organization
			work_ledger_entry.date = self.date
			work_ledger_entry.work_assignment = self.name
			work_ledger_entry.hours_change = member.duration
			work_ledger_entry.insert()

	def delete_work_ledger_entry(self):
		frappe.delete_doc("Work Ledger Entry", {"work_assignment": self.name})
