# -*- coding: utf-8 -*-
# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

from landa.organization_management.doctype.external_function.external_function import (
	get_active_external_functions,
)


class ExternalFunctionCategory(Document):
	def get_external_contact_names(self):
		"""Return a list of external contacs to whom this External Function Category applies."""
		filters = {"external_function_category": self.name}
		external_contact_names = get_active_external_functions(
			filters=filters, pluck="external_contact"
		)
		return list(set(external_contact_names))
