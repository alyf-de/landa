import frappe
from frappe import _


def validate_company_price_list(company: str, price_list: str):
	if not price_list:
		return

	if frappe.db.get_value("Price List", price_list, "company") != company:
		frappe.throw(_("Price List {0} is not valid for Company {1}.").format(price_list, company))


def validate_company_customer(company: str, customer: str):
	if not customer or not company:
		return

	company_abbr = frappe.db.get_value("Company", company, "abbr")
	customer_organization = frappe.db.get_value("Customer", customer, "organization")
	if company_abbr not in customer_organization:
		frappe.throw(_("Customer {0} is not valid for Company {1}.").format(customer, company))
