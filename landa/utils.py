import frappe
from frappe import _


def get_new_name(prefix, company, doctype):
	"""
	Create a document name like prefix-company-year-####.

	For example 'ZAHL-AVS-2021-0001'.
	"""
	from frappe.model.naming import make_autoname
	from frappe.utils.data import nowdate

	company_abbr = frappe.get_value("Company", company, "abbr")
	current_year = nowdate()[:4]  # note: y10k problem
	return make_autoname(f"{prefix}-{company_abbr}-{current_year}-.####", doctype)


def welcome_email():
	lang = frappe.db.get_single_value("System Settings", "language")
	site_name = "LANDA"
	title = _("Welcome to {0}", lang=lang).format(site_name)
	return title
