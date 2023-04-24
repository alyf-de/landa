import frappe
from frappe.permissions import add_user_permission, clear_user_permissions_for_doctype
from pypika.functions import Length

from landa.organization_management.doctype.member_function.member_function import (
	apply_active_member_functions,
)


def execute():
	table = frappe.qb.DocType("LANDA Member")
	for member_name, user, organization in (
		frappe.qb.from_(table)
		.select(table.name, table.user, table.organization)
		.where(Length(table.organization) > 7)
		.where(table.user.notnull())
		.where(table.user != "")
		.run()
	):
		clear_user_permissions_for_doctype("Organization", user)
		add_user_permission("Organization", organization, user, ignore_permissions=True)
		apply_active_member_functions({"member": member_name})
