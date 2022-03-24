from typing import Optional
import frappe


def report_query(user: Optional[str]) -> str:
	"""Users can see their own reports and standard reports.

	Users with role "System Manager" (and Administrator) can see all reports.
	"""
	if not user:
		user = frappe.session.user

	if "System Manager" in frappe.get_roles(frappe.session.user):
		return ""

	# todos that belong to user or assigned by user
	return "(`tabReport`.owner = {user} or `tabReport`.is_standard = 'Yes')".format(
		user=frappe.db.escape(user)
	)
