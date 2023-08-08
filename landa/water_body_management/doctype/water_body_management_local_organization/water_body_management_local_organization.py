# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt


# import frappe
from frappe.model.document import Document

from landa.water_body_management.doctype.water_body.water_body import rebuild_water_body_cache


class WaterBodyManagementLocalOrganization(Document):
	def on_update(self):
		rebuild_water_body_cache(self.fishing_area)

	def on_trash(self):
		rebuild_water_body_cache(self.fishing_area)
