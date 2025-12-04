# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WaterBodySpecialProvisionTable(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		short_code: DF.Data | None
		water_body_special_provision: DF.Link
	# end: auto-generated types
	pass
