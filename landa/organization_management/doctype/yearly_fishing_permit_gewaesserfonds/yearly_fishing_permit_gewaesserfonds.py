# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import cint

# Index (starting at 1) of each entry is the `n` in the legacy
# `has_special_yearly_fishing_permit_{n}` fields of LANDA Member.
ASSOCIATIONS_AND_STATES = [
	"Sachsen-Anhalt",
	"Brandenburg",
	"Berlin",
	"Mecklenburg-Vorpommern",
	"Saalekaskade",
	"LAVT",
	"VANT",
]


class YearlyFishingPermitGewaesserfonds(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		association_or_state: DF.Literal[
			"Sachsen-Anhalt",
			"Brandenburg",
			"Berlin",
			"Mecklenburg-Vorpommern",
			"Saalekaskade",
			"LAVT",
			"VANT",
		]
		member: DF.Link
		member_first_name: DF.Data | None
		member_last_name: DF.Data | None
		number: DF.Data | None
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
			"Yearly Fishing Permit Gewaesserfonds",
			{
				"name": ("!=", self.name),
				"member": self.member,
				"year": self.year,
				"association_or_state": self.association_or_state,
			},
		):
			frappe.throw(
				_("{0} already has a {1} permit for {2}.").format(
					self.member, self.association_or_state, self.year
				),
				exc=frappe.DuplicateEntryError,
			)

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


def update_gewaesserfonds_permit_statuses():
	for permit in get_gewaesserfonds_permits_to_update():
		doc = frappe.get_doc("Yearly Fishing Permit Gewaesserfonds", permit.name)
		if doc.status == doc.get_status():
			continue
		try:
			doc.save()
		except Exception:
			frappe.log_error(
				title=f"Failed to update status of Yearly Fishing Permit Gewaesserfonds {doc.name}",
			)


def get_gewaesserfonds_permits_to_update():
	this_year = datetime.now().year

	return frappe.get_all(
		"Yearly Fishing Permit Gewaesserfonds",
		filters={"year": ["in", [this_year - 1, this_year, this_year + 1]]},
		fields=["name", "year", "status"],
	)


@frappe.whitelist(methods=["POST"])
def bulk_create(year: str | int, association_or_state: str, members: str):
	parsed_members = json.loads(members)
	year = cint(year)

	assert isinstance(parsed_members, list), "Members must be a list"
	assert all(isinstance(member, str) for member in parsed_members), "Members must be a list of strings"
	assert association_or_state in ASSOCIATIONS_AND_STATES, "Unknown association or state"

	title = _("Creating Yearly Fishing Permits Gewaesserfonds...")
	frappe.publish_progress(percent=0, title=title, doctype="LANDA Member")

	num_members = len(parsed_members)
	num_skipped = 0
	for i, member in enumerate(parsed_members):
		frappe.publish_progress(
			percent=i * 100 / num_members,
			title=title,
			doctype="LANDA Member",
			description=member,
		)
		permit = frappe.new_doc("Yearly Fishing Permit Gewaesserfonds")
		permit.member = member
		permit.organization = frappe.db.get_value("LANDA Member", member, "organization")
		permit.year = year
		permit.association_or_state = association_or_state
		try:
			permit.insert()
		except (frappe.DuplicateEntryError, frappe.ValidationError):
			frappe.clear_messages()
			num_skipped += 1
			continue

	frappe.publish_progress(percent=100, title=title, doctype="LANDA Member", description=_("Done"))

	return {"num_created": num_members - num_skipped, "num_skipped": num_skipped}
