# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import date_diff, today


class MemberFunction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		end_date: DF.Date | None
		member: DF.Link
		member_first_name: DF.Data | None
		member_function_category: DF.Link
		member_last_name: DF.Data | None
		organization: DF.Link | None
		organization_name: DF.Data | None
		start_date: DF.Date | None
		status: DF.Literal["Planned", "Active", "Inactive"]

	# end: auto-generated types
	def before_validate(self):
		self.status = self.get_status()

	def validate(self):
		if self.start_date and self.end_date and date_diff(self.start_date, self.end_date) > 0:
			frappe.throw(_("End Date cannot be before Start Date."))

		self.validate_member_function_category()
		self.validate_unique_roles()

	def get_access_level(self) -> str | None:
		"""Return the access level of the linked Member Function Category."""
		return frappe.get_value("Member Function Category", self.member_function_category, "access_level")

	def validate_member_function_category(self):
		"""Check if the current user is allowed to set the member function category.

		The current user needs to have certain roles to grant access at a certain level:

		- Access at level "Local Group" can be granted by anyone who can create Member Functions
		- LANDA State Organization Employee: can grant access on any level
		- LANDA Regional Organization Management: can grant access at level Regional Organization and below
		- LANDA Local Organization Management: can grant access at level Local Organization and below

		Raise a permission error for all other cases.
		"""

		def has_role(role: str) -> bool:
			"""Check if the current user has the given role."""
			return role in frappe.get_roles(frappe.session.user)

		access_level = self.get_access_level()

		if access_level == "Local Group":
			return

		if access_level == "State Organization" and has_role("LANDA State Organization Employee"):
			return

		if access_level == "Regional Organization" and (
			has_role("LANDA State Organization Employee")
			or has_role("LANDA Regional Organization Management")
		):
			return

		if access_level == "Local Organization" and (
			has_role("LANDA State Organization Employee")
			or has_role("LANDA Regional Organization Management")
			or has_role("LANDA Local Organization Management")
		):
			return

		frappe.throw(
			_("No permission to set Member Function Category {0}").format(self.member_function_category),
			frappe.PermissionError,
		)

	def on_update(self):
		self.update_user_roles()

	def on_trash(self):
		self.status = "Inactive"
		self.update_user_roles()

	def update_user_roles(self):
		member_function_category = frappe.get_doc("Member Function Category", self.member_function_category)
		if self.status == "Active":
			member_function_category.add_roles_and_permissions(self.member)
		else:
			member_function_category.remove_roles_and_permissions(
				self.member, disabled_member_function=self.name
			)

	def get_status(self):
		if self.is_planned():
			return "Planned"
		elif self.is_inactive():
			return "Inactive"
		else:
			return "Active"

	def is_planned(self):
		return self.start_date and date_diff(today(), self.start_date) < 0

	def is_inactive(self):
		return self.end_date and date_diff(today(), self.end_date) > 0

	def validate_unique_roles(self):
		only_one, category_name = frappe.db.get_value(
			"Member Function Category", self.member_function_category, ["only_one_per_organization", "name"]
		)

		if not only_one or self.status != "Active":
			return

		existing_member_functions = frappe.db.exists(
			"Member Function",
			{
				"organization": self.organization,
				"member_function_category": self.member_function_category,
				"name": ["!=", self.name],  # Exclude this document from the search
				"status": "Active",
			},
		)
		if existing_member_functions:
			frappe.throw(
				_("The Member Function Category {0} can only be assigned once per organization.").format(
					frappe.bold(category_name)
				)
			)


def update_member_function_status():
	# Expire first, so a successor does not conflict with its predecessor in `validate_unique_roles`.
	disable_expired_member_functions()
	activate_planned_member_functions()


def disable_expired_member_functions():
	save_member_functions(member_function.name for member_function in get_expired_member_functions())


def activate_planned_member_functions():
	save_member_functions(
		frappe.get_all(
			"Member Function",
			filters=[["status", "=", "Planned"], ["start_date", "<=", today()]],
			pluck="name",
		)
	)


def save_member_functions(names):
	"""Save each Member Function to update its status, roles and permissions."""
	for name in names:
		# One invalid Member Function must not block the others.
		frappe.db.savepoint("save_member_function")
		try:
			doc = frappe.get_doc("Member Function", name)
			doc.save()
		except Exception:
			frappe.db.rollback(save_point="save_member_function")
			frappe.log_error(f"Could not update the status of Member Function {name}")


def apply_active_member_functions(filters):
	for member_function in get_active_member_functions(filters=filters, pluck="name"):
		doc = frappe.get_doc("Member Function", member_function)
		doc.save()


def get_expired_member_functions():
	return frappe.get_all(
		"Member Function",
		filters=[
			["end_date", "<", today()],
			["end_date", "is", "set"],
		],
	)


def get_active_member_functions(filters: dict = None, pluck: str = None):
	return frappe.get_all(
		"Member Function",
		filters=filters,
		or_filters=[["end_date", "is", "not set"], ["end_date", ">=", today()]],
		pluck=pluck,
	)
