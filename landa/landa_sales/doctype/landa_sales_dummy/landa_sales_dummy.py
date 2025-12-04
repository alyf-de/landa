# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LANDASalesDummy(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		dummy: DF.Data | None

	# end: auto-generated types
	def db_insert(self):
		pass

	def load_from_db(self):
		pass

	def db_update(self):
		pass

	def get_list(self, args):
		pass
