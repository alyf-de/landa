# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import date_diff, getdate, today


class LeaseContract(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.water_body_management.doctype.lease_contract_rent.lease_contract_rent import (
			LeaseContractRent,
		)

		additional_information: DF.SmallText | None
		currency: DF.Link | None
		end_date: DF.Date | None
		fishing_area: DF.Link | None
		landlord_new: DF.Link | None
		lease_contract_rent: DF.Table[LeaseContractRent]
		lease_object: DF.Link | None
		organization: DF.Link
		organization_name: DF.Data | None
		payment_due_date: DF.Date | None
		payment_reference: DF.Data | None
		payment_type: DF.Literal["Credit Transfer", "Direct Debit"]
		start_date: DF.Date | None
		status: DF.Literal["Planned", "Active", "Inactive"]
		water_body: DF.Link
		water_body_title: DF.Data | None

	# end: auto-generated types
	def before_validate(self):
		self.status = self.get_status()

	def validate(self):
		if self.organization != frappe.db.get_value("Water Body", self.water_body, "organization"):
			frappe.throw(_("Lease Contract must belong to the same regional Organization as the Water Body."))

		self.validate_rent_dates()

	def validate_rent_dates(self):
		self.validate_from_to_dates("start_date", "end_date")
		for row_a in self.lease_contract_rent:
			row_a.validate_from_to_dates("from_date", "to_date")
			if row_a.from_date and self.start_date and getdate(row_a.from_date) < getdate(self.start_date):
				frappe.throw(
					_(
						"Lease Contract Rent row {0} cannot start before the Lease Contract's start date."
					).format(row_a.idx)
				)

			if row_a.to_date and self.end_date and getdate(row_a.to_date) > getdate(self.end_date):
				frappe.throw(
					_("Lease Contract Rent row {0} cannot end after the Lease Contract's end date.").format(
						row_a.idx
					)
				)

			for row_b in self.lease_contract_rent:
				if row_b.name == row_a.name:
					continue

				if not row_b.from_date or not row_b.to_date:
					continue

				if (
					row_a.to_date
					and (getdate(row_b.from_date) <= getdate(row_a.to_date) <= getdate(row_b.to_date))
				) or (
					row_a.from_date
					and (getdate(row_b.from_date) <= getdate(row_a.from_date) <= getdate(row_b.to_date))
				):
					frappe.throw(
						_("Lease Contract Rent row {0} overlaps with row {1}.").format(row_a.idx, row_b.idx)
					)

	def get_status(self):
		if self.is_planned():
			return "Planned"
		elif self.is_inactive():
			return "Inactive"
		else:
			return "Active"

	def is_planned(self):
		return self.start_date and date_diff(today(), self.start_date) < 0

	def is_inactive(self):
		return self.end_date and date_diff(today(), self.end_date) > 0


def deactivate_lease_contracts():
	for lease_contract in get_lease_contracts_to_deactivate():
		frappe.db.set_value("Lease Contract", lease_contract, "status", "Inactive")


def activate_lease_contracts():
	for lease_contract in get_lease_contracts_to_activate():
		frappe.db.set_value("Lease Contract", lease_contract, "status", "Active")


def get_lease_contracts_to_deactivate():
	return frappe.get_all(
		"Lease Contract",
		filters=[
			["end_date", "<", today()],
			["end_date", "is", "set"],
			["status", "!=", "Inactive"],
		],
		pluck="name",
	)


def get_lease_contracts_to_activate():
	return frappe.get_all(
		"Lease Contract",
		filters=[
			["start_date", "<=", today()],
			["status", "!=", "Active"],
		],
		or_filters=[["end_date", "is", "not set"], ["end_date", ">=", today()]],
		pluck="name",
	)
