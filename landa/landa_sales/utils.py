from typing import TYPE_CHECKING

import frappe
from frappe import _

if TYPE_CHECKING:
	from erpnext.controllers.selling_controller import SellingController


def validate_company_price_list(company: str, price_list: str):
	if not price_list:
		return

	if frappe.flags.in_test and price_list.startswith("_Test"):
		return

	if frappe.db.get_value("Price List", price_list, "company") != company:
		frappe.throw(_("Price List {0} is not valid for Company {1}.").format(price_list, company))


def validate_company_customer(company: str, customer: str):
	if not customer or not company:
		return

	company_abbr = frappe.db.get_value("Company", company, "abbr")
	customer_organization = frappe.db.get_value("Customer", customer, "organization")
	if customer_organization and (company_abbr not in customer_organization):
		frappe.throw(_("Customer {0} is not valid for Company {1}.").format(customer, company))


def validate_year_of_settlement(doc: "SellingController"):
	if not doc.year_of_settlement:
		return

	for item in doc.items:
		from_year, to_year = frappe.db.get_value("Item", item.item_code, ["valid_from_year", "valid_to_year"])

		if (from_year and doc.year_of_settlement < from_year) or (
			to_year and doc.year_of_settlement > to_year
		):
			frappe.throw(
				_("Row {0}: Item {1} is not valid for year of settlement {2}.").format(
					item.idx, frappe.bold(item.item_name), frappe.bold(doc.year_of_settlement)
				)
			)
