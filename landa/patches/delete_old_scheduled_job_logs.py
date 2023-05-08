import frappe
from frappe.utils import add_days, now


def execute():
	date_a_month_ago = add_days(now(), -30)  # datetime
	frappe.db.delete("Scheduled Job Log", {"creation": ["<", date_a_month_ago]})
