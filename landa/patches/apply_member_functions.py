import frappe
from frappe.utils import update_progress_bar
from landa.organization_management.doctype.member_function.member_function import (
	apply_active_member_functions,
)


def execute():
	members = frappe.get_all(
		"User", filters={"landa_member": ("is", "set"), "enabled": 1}, pluck="landa_member"
	)
	total = len(members)
	for i, member_name in enumerate(members):
		update_progress_bar("Applying member functions", i, total)
		apply_active_member_functions({"member": member_name})
