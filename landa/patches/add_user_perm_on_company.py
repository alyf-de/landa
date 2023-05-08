import frappe
from frappe.permissions import add_user_permission

from landa.utils import get_default_company


def execute():
	"""Restrict all LANDA Members to their regional organization's company."""
	members = frappe.get_all(
		"LANDA Member", fields=["organization", "user"], filters={"user": ("is", "set")}
	)

	for member in members:
		company = None
		company = get_default_company(member.organization)
		add_user_permission("Company", company, member.user, ignore_permissions=True)
