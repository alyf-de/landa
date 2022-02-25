# -*- coding: utf-8 -*-
# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe

from frappe import _
from frappe.utils.data import today
from frappe.utils.data import date_diff
from frappe.model.document import Document


class LeaseContract(Document):
	def before_validate(self):
		self.update_is_active()

	def validate(self):
		if self.start_date and self.end_date:
			if date_diff(self.start_date, self.end_date) > 0:
				frappe.throw(_("End Date cannot be before Start Date."))


	def on_trash(self):
		self.status = "Inactive"

	def update_is_active(self):
		if self.is_planned():
			self.status = "Planned"
		elif self.is_inactive():
			self.status = "Inactive"
		else:
			self.status = "Active"

	def is_planned(self):
		return self.start_date and date_diff(today(), self.start_date) < 0

	def is_inactive(self):
		return self.end_date and date_diff(today(), self.end_date) > 0


def disable_expired_lease_contracts():
	for lease_contract in get_expired_lease_contracts():
		doc = frappe.get_doc("Lease Contract", lease_contract.name)
		doc.save()


def apply_active_lease_contracts(filters):
	for lease_contract in get_active_lease_contracts(filters=filters, pluck="name"):
		doc = frappe.get_doc("Lease Contract", lease_contract)
		doc.save()


def get_expired_lease_contracts():
	return frappe.get_all(
		"Lease Contract",
		filters=[
			["end_date", "<", today()],
			["end_date", "is", "set"],
		],
	)


def get_active_lease_contracts(filters: dict = None, pluck: str = None):
	return frappe.get_all(
		"Lease Contract",
		filters=filters,
		or_filters=[["end_date", "is", "not set"], ["end_date", ">=", today()]],
		pluck=pluck,
	)
