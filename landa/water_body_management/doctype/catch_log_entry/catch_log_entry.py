# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _, get_roles
from frappe.model.document import Document
from frappe.model.workflow import get_workflow


class CatchLogEntry(Document):
	def before_insert(self):
		user_roles = set(get_roles(frappe.session.user))
		regional_origin = {
			"LANDA Regional Organization Management",
			"LANDA Regional Water Body Management",
			"LANDA State Organization Employee",
			"System Manager",
			"Administrator",
		}
		if regional_origin.intersection(user_roles):
			self.origin_of_catch_log_entry = "Regionalverband"
		else:
			self.origin_of_catch_log_entry = "Verein"

	def validate(self):
		# water_body = get_doc("Water Body", self.water_body)
		# main_species = [row.fish_species for row in water_body.fish_species]
		blacklisted_species = frappe.get_all(
			"Blacklisted Fish Species Table", {"parent": self.water_body}, pluck="fish_species"
		)

		for row in self.fish_catches:
			row.plausible = int(row.validate_weight())

			if blacklisted_species and (row.fish_species in blacklisted_species):
				frappe.throw(
					_("Row {0}: Fish Species {1} cannot occur in {2}").format(
						row.idx, frappe.bold(row.fish_species), frappe.bold(self.water_body_title)
					),
					title=_("Invalid Species"),
				)

	def before_save(self):
		if self.is_new():
			return

		self.check_workflow_perms()

	def on_trash(self):
		self.check_workflow_perms()

	def check_workflow_perms(self):
		"""Raise a PermissionError if the user is not allowed to edit the document
		in the current workflow state.
		"""
		workflow = get_workflow(self.doctype)
		workflow_state = self.db_get(workflow.workflow_state_field)
		frappe.only_for(
			roles=[row.allow_edit for row in workflow.states if row.state == workflow_state],
		)
