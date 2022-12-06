import frappe
from frappe.utils import update_progress_bar

from landa.organization_management.doctype.member_function_category.member_function_category import (
	apply_roles,
)
from landa.utils import autocommit


def execute():
	with autocommit():
		users = frappe.get_all(
			"User", filters={"landa_member": ("is", "set"), "enabled": 1}, fields=["name", "landa_member"]
		)
		total = len(users)
		for i, (user, member) in enumerate(users):
			update_progress_bar("Applying member functions", i, total)
			apply_roles(member, user)
