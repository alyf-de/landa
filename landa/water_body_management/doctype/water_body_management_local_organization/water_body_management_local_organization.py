# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt


# import frappe
from frappe.model.document import Document

from landa.water_body_management.doctype.water_body.water_body import rebuild_water_body_cache


class WaterBodyManagementLocalOrganization(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.water_body_management.doctype.water_body_local_contact_table.water_body_local_contact_table import (
			WaterBodyLocalContactTable,
		)

		disabled: DF.Check
		fishing_area: DF.Link | None
		note: DF.SmallText | None
		organization: DF.Link
		organization_name: DF.Data | None
		regional_organization: DF.Link | None
		water_body: DF.Link
		water_body_local_contact_table: DF.Table[WaterBodyLocalContactTable]
		water_body_title: DF.Data | None

	# end: auto-generated types
	def on_update(self):
		rebuild_water_body_cache()

	def after_delete(self):
		rebuild_water_body_cache()
