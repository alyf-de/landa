# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Landlord(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_information: DF.Text | None
		iban: DF.Data | None
		landlord_name: DF.Data
		regional_organization: DF.Link
	# end: auto-generated types
	pass
