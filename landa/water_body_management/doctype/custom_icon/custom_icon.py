# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomIcon(Document):
	def autoname(self):
		self.name = "-".join(self.title.lower().split(" "))


def get_icon_map():
	icons = frappe.get_all("Custom Icon", fields=["name", "icon"])
	return {icon.name: icon.icon for icon in icons}
