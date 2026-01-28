# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime


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