# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import cint

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
		if self.year:
			self.year = cint(self.year)
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


@frappe.whitelist()
def bulk_create(year: str | int, members: str):
	parsed_members = json.loads(members)
	year = cint(year)

	assert isinstance(parsed_members, list), "Members must be a list"
	assert all(isinstance(member, str) for member in parsed_members), "Members must be a list of strings"
	assert isinstance(year, int), "Year must be an integer"

	frappe.publish_progress(
		percent=0,
		title=_("Creating Supporting Memberships..."),
		doctype="LANDA Member",
	)

	num_members = len(parsed_members)
	num_skipped = 0
	for i, member in enumerate(parsed_members):
		frappe.publish_progress(
			percent=i * 100 / num_members,
			title=_("Creating Supporting Memberships..."),
			doctype="LANDA Member",
			description=member,
		)
		supporting_membership = frappe.new_doc("Supporting Membership")
		supporting_membership.member = member
		supporting_membership.organization = frappe.db.get_value("LANDA Member", member, "organization")
		supporting_membership.year = year
		try:
			supporting_membership.insert()
		except (frappe.DuplicateEntryError, frappe.ValidationError):
			frappe.clear_messages()
			num_skipped += 1
			continue

	frappe.publish_progress(
		percent=100,
		title=_("Creating Supporting Memberships..."),
		doctype="LANDA Member",
		description=_("Done"),
	)

	return {"num_created": num_members - num_skipped, "num_skipped": num_skipped}
