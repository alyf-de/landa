# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FishingArea(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		area_code: DF.Data
		area_name: DF.Data
		organization: DF.Link
		organization_name: DF.Data | None
	# end: auto-generated types
	pass
