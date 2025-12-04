# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WaterBodyRules(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		imprint: DF.TextEditor | None
		privacy_policy: DF.TextEditor | None
		water_body_rules: DF.TextEditor | None
	# end: auto-generated types
	pass
