# Copyright (c) 2026, ALYF GmbH and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document

from landa.utils import get_current_member_data
from landa.water_body_management.doctype.stocking_measure_import_history.stocking_measure_import_history import (
	StockingMeasureImportHistory,
)


class StockingMeasureImport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from landa.water_body_management.doctype.stocking_measure_import_history.stocking_measure_import_history import (
			StockingMeasureImportHistory,
		)
		from landa.water_body_management.doctype.stocking_measure_import_item.stocking_measure_import_item import (
			StockingMeasureImportItem,
		)

		date: DF.Date
		history: DF.Table[StockingMeasureImportHistory]
		items: DF.Table[StockingMeasureImportItem]
		organization: DF.Link
		water_body: DF.Link
		year: DF.Int
	# end: auto-generated types

	def load_from_db(self):
		current_member_data = get_current_member_data()
		now = datetime.now()
		super(Document, self).__init__(
			{
				"name": self.name or frappe.generate_hash(length=8),
				"organization": current_member_data.regional_organization,
				"date": now.date(),
				"year": now.year,
				"creation": now,
				"modified": now,
				"owner": frappe.session.user,
				"modified_by": frappe.session.user,
				"history": self._get_history(),
			}
		)

	def load_doc_before_save(self, *args, **kwargs):
		"""Virtual doctype: no DB row to compare against."""
		self._doc_before_save = None

	def db_insert(self, *args, **kwargs):
		self._create_stocking_measures()
		self.history = self._get_history()
		return self.as_dict()

	def db_update(self, *args, **kwargs):
		self._create_stocking_measures()
		self.history = self._get_history()

	def _create_stocking_measures(self):
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

	def _get_history(self):
		now = datetime.now()
		records = frappe.get_list(
			"Stocking Measure",
			filters={
				"owner": frappe.session.user,
				"creation": (">", now - timedelta(days=1)),
			},
			fields=[
				"name as stocking_measure",
				"owner",
				"modified",
				"modified_by",
				"creation",
				"water_body",
				"fish_species",
				"fish_type_for_stocking",
				"weight",
			],
			order_by="creation desc",
		)
		return [
			StockingMeasureImportHistory({"doctype": "Stocking Measure Import History", **record})
			for record in records
		]

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
