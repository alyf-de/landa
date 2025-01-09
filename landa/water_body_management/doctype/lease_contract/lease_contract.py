# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import date_diff, today


class LeaseContract(Document):
	def before_validate(self):
		self.status = self.get_status()

	def validate(self):
		if self.start_date and self.end_date and date_diff(self.start_date, self.end_date) > 0:
			frappe.throw(_("End Date cannot be before Start Date."))

		if self.organization != frappe.db.get_value("Water Body", self.water_body, "organization"):
			frappe.throw(
				_("Lease Contract must belong to the same regional Organization as the Water Body.")
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
