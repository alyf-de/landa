# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Substring
from pypika.functions import Coalesce
from pypika.terms import Not


def execute(filters=None):
	return get_columns(), get_data()


def get_data():
	User = frappe.qb.DocType("User")
	UserPermission = frappe.qb.DocType("User Permission")

	org_permissions = (
		frappe.qb.from_(UserPermission)
		.select(UserPermission.user, UserPermission.for_value)
		.where(UserPermission.allow == "Organization")
		.where(UserPermission.apply_to_all_doctypes == 1)
	)

	query = (
		frappe.qb.from_(User)
		.left_join(org_permissions)
		.on(User.name == org_permissions.user)
		.select(
			User.name,
			User.organization,
			Coalesce(org_permissions.for_value, "All Organizations").as_("permissions_for"),
		)
		.where(User.name.notin(["Administrator", "Guest"]))
		.where(User.enabled == 1)
		.where(
			(Substring(org_permissions.for_value, 1, 7) != Substring(User.organization, 1, 7))
			| (org_permissions.for_value.isnull())
		)
		.where(
			# Exclude lines like "Member of AVL-000. Permissions for AVL" (regional org management)
			Not(
				(Substring(User.organization, 5, 7) == "000")
				& (Substring(User.organization, 1, 3) == org_permissions.for_value)
			)
		)
		.orderby(User.name)
	)

	return query.run()


def get_columns():
	return [
		{
			"fieldname": "user",
			"label": _("User"),
			"fieldtype": "Link",
			"options": "User",
		},
		{
			"fieldname": "member_of",
			"label": _("Member of"),
			"fieldtype": "Link",
			"options": "Organization",
		},
		{
			"fieldname": "permissions_for",
			"label": _("Permissions for"),
			"fieldtype": "Data",
		},
	]
