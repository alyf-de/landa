# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document

from landa.organization_management.membership_permit_validation import (
	validate_no_active_yearly_fishing_permit,
)


class SupportingMembership(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		member: DF.Link
		member_first_name: DF.Data | None
		member_last_name: DF.Data | None
		organization: DF.Link | None
		organization_name: DF.Data | None
		status: DF.Literal["Planned", "Active", "Inactive"]
		year: DF.Int
	# end: auto-generated types

	def before_validate(self):
		self.status = self.get_status()

	def validate(self):
		if frappe.db.exists(
			"Supporting Membership",
			{
				"name": ("!=", self.name),
				"member": self.member,
				"year": self.year,
			},
		):
			frappe.throw(
				_(
					"Supporting Membership already exists for member {0} and year {1}. Please delete the existing membership before creating a new one."
				).format(self.member, self.year),
				exc=frappe.DuplicateEntryError,
			)

		if self.member and self.status == "Active":
			validate_no_active_yearly_fishing_permit(self.member, self.year)

	def on_trash(self):
		self.status = "Inactive"

	def get_status(self):
		if self.is_planned():
			return "Planned"
		elif self.is_inactive():
			return "Inactive"
		else:
			return "Active"

	def is_planned(self):
		return self.year and self.year > datetime.now().year

	def is_inactive(self):
		return self.year and self.year < datetime.now().year


def update_supporting_membership_statuses():
	for supporting_membership in get_supporting_memberships_to_update():
		doc = frappe.get_doc("Supporting Membership", supporting_membership.name)
		if doc.status == doc.get_status():
			continue
		doc.save()


def get_supporting_memberships_to_update():
	this_year = datetime.now().year

	return frappe.get_all(
		"Supporting Membership",
		filters={"year": ["in", [this_year - 1, this_year, this_year + 1]]},
		fields=["name", "year", "status"],
	)
