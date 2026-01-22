# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class StockingPlanImport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.water_body_management.doctype.stocking_plan_import_item.stocking_plan_import_item import (
			StockingPlanImportItem,
		)

		date: DF.Date
		items: DF.Table[StockingPlanImportItem]
		organization: DF.Link
		water_body: DF.Link
		year: DF.Int
	# end: auto-generated types

	def db_insert(self, *args, **kwargs):
		for item in self.items:
			frappe.get_doc(
				{
					"doctype": "Stocking Measure",
					"organization": self.organization,
					"water_body": self.water_body,
					"year": self.year,
					"date": self.date,
					"fish_species": item.fish_species,
					"fish_type_for_stocking": item.fish_type_for_stocking,
					"weight": item.weight,
					"quantity": item.quantity or 0,
					"supplier": item.supplier,
					"status": "In Progress",
				}
			).insert()

		frappe.msgprint(
			_("{0} Stocking Measure(s) created").format(len(self.items)),
			alert=True,
			indicator="green",
		)

	def load_from_db(self):
		pass

	def db_update(self):
		pass

	def delete(self):
		pass

	@staticmethod
	def get_list(args):
		pass

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass
