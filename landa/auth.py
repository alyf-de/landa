import frappe
from frappe.rate_limiter import rate_limit


@frappe.whitelist()
@rate_limit(limit=100, seconds=60 * 60)
def check_password(password: str) -> bool:
	if not isinstance(password, str):
		return False

	try:
		frappe.local.login_manager.check_password(frappe.session.user, password)
		return True
	except frappe.AuthenticationError:
		return False
