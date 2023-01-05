# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from frappe.model.document import Document


class YearlyFishingPermit(Document):
	def on_update(self):
		if self.has_permission("submit"):
			self.submit()
