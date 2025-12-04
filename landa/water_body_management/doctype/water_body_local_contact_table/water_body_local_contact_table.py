# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WaterBodyLocalContactTable(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		first_name: DF.Data | None
		landa_member: DF.Link
		last_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass
