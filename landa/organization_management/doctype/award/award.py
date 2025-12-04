# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Award(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		award_type: DF.Link
		issue_date: DF.Date | None
		member: DF.Link
		organization: DF.Link | None
		organization_name: DF.Data | None
		recipient_first_name: DF.Data | None
		recipient_last_name: DF.Data | None
	# end: auto-generated types
	pass
