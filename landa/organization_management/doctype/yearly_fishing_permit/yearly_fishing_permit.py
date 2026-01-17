# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document


class YearlyFishingPermit(Document):
	def before_insert(self):
		if not self.member:
			frappe.throw(_("Please set the corresponding LANDA Member"))

		self.number = f"{self.member}-{self.year}"

	def validate(self):
		if self.member:
			self.first_name, self.last_name, self.organization = frappe.db.get_value(
				"LANDA Member", self.member, ["first_name", "last_name", "organization"]
			)

		duplicate_types = {"SALMO", "ALLG", "KOMBI"}
		if self.type == "SALMO":
			duplicate_types.remove("ALLG")
		elif self.type == "ALLG":
			duplicate_types.remove("SALMO")

		if frappe.db.exists(
			"Yearly Fishing Permit",
			{
				"name": ("!=", self.name),
				"member": self.member,
				"year": self.year,
				"docstatus": ("!=", 2),
				"type": ("in", duplicate_types),
			},
		):
			frappe.throw(
				_(
					"Yearly Fishing Permit already exists for member {0} and year {1}. Please delete or cancel the existing permit before creating a new one."
				).format(self.member, self.year),
				exc=frappe.DuplicateEntryError,
			)

		current_year = datetime.now().year
		if int(self.year) not in [current_year, current_year + 1]:
			frappe.throw(_("Year must be either the current year or the next year."))

	def on_update(self):
		if self.has_permission("submit") and self.docstatus == 0:
			self.submit()


@frappe.whitelist()
def bulk_create(permit_type: str, year: str, members: str):
	parsed_members = json.loads(members)

	assert isinstance(parsed_members, list), "Members must be a list"
	assert all(
		isinstance(member, str) for member in parsed_members
	), "Members must be a list of strings"
	assert isinstance(permit_type, str), "Permit type must be a string"
	assert isinstance(year, str), "Year must be a string"

	frappe.publish_progress(
		percent=0,
		title=_("Creating Yearly Fishing Permits..."),
		doctype="LANDA Member",
	)

	num_members = len(parsed_members)
	for i, member in enumerate(parsed_members):
		frappe.publish_progress(
			percent=i * 100 / num_members,
			title=_("Creating Yearly Fishing Permits..."),
			doctype="LANDA Member",
			description=member,
		)
		yfp = frappe.new_doc("Yearly Fishing Permit")
		yfp.member = member
		yfp.year = year
		yfp.type = permit_type
		yfp.insert()

	frappe.publish_progress(
		percent=100,
		title=_("Creating Yearly Fishing Permits..."),
		doctype="LANDA Member",
		description=_("Done"),
	)

	return num_members
