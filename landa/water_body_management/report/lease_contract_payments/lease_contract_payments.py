# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.data import getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(
		filters["year"],
		filters.get("water_body"),
		filters.get("fishing_area"),
		filters.get("lease_object"),
		filters.get("landlord"),
	)
	return columns, list(data)


def get_columns():
	return [
		{
			"fieldname": "water_body",
			"label": _("Water Body"),
			"fieldtype": "Link",
			"options": "Water Body",
		},
		{
			"fieldname": "water_body_title",
			"label": _("Water Body Title"),
			"fieldtype": "Data",
			"width": "200",
		},
		{
			"fieldname": "fishing_area",
			"label": _("Fishing Area"),
			"fieldtype": "Link",
			"options": "Fishing Area",
		},
		{
			"fieldname": "lease_object",
			"label": _("Lease Object"),
			"fieldtype": "Link",
			"options": "Lease Object",
			"width": "150",
		},
		{
			"fieldname": "payment_recipient",
			"label": _("Payment Recipient"),
			"fieldtype": "Data",
			"width": "200",
		},
		{
			"fieldname": "iban",
			"label": _("IBAN"),
			"fieldtype": "Data",
			"width": "200",
		},
		{
			"fieldname": "rent",
			"label": _("Rent"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": "150",
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1,
		},
		{
			"fieldname": "payment_reference",
			"label": _("Payment Reference"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "payment_type",
			"label": _("Payment Type"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "payment_due_date",
			"label": _("Payment Due Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "lease_contract",
			"label": _("Lease Contract"),
			"fieldtype": "Link",
			"options": "Lease Contract",
		},
	]


def get_data(
	year: int,
	water_body: str | None,
	fishing_area: str | None,
	lease_object: str | None,
	landlord: str | None,
):
	year_end = getdate(f"{year}-12-31")
	year_start = getdate(f"{year}-01-01")
	filters = [
		["start_date", "<=", year_end],
		["end_date", ">=", year_start],
		["Lease Contract Rent", "from_date", "<=", year_end],
		["Lease Contract Rent", "to_date", ">=", year_start],
	]

	if water_body:
		filters.append(["water_body", "=", water_body])

	if fishing_area:
		filters.append(["fishing_area", "=", fishing_area])

	if lease_object:
		filters.append(["lease_object", "=", lease_object])

	if landlord:
		filters.append(["landlord_new", "=", landlord])

	for lease_contract in frappe.get_list(
		"Lease Contract",
		filters=filters,
		fields=[
			"name",
			"water_body",
			"water_body_title",
			"fishing_area",
			"currency",
			"lease_object",
			"payment_reference",
			"payment_type",
			"payment_due_date",
			"landlord_new",
			"`tabLease Contract Rent`.from_date",
			"`tabLease Contract Rent`.to_date",
			"`tabLease Contract Rent`.rent_per_year",
		],
		order_by="payment_due_date ASC",
	):
		# Check if we need to calculate partial rent
		# Only calculate partial rent if the contract period doesn't fully cover the year
		contract_start_in_year = max(year_start, lease_contract.from_date)
		contract_end_in_year = min(year_end, lease_contract.to_date)

		if lease_contract.from_date > year_start or lease_contract.to_date < year_end:
			# Calculate partial rent using actual days in the year (handles leap years)
			days_in_contract_period = (contract_end_in_year - contract_start_in_year).days + 1
			days_in_year = (year_end - year_start).days + 1

			rent = round(
				lease_contract.rent_per_year * round(days_in_contract_period / days_in_year, 2),
				2,
			)
		else:
			rent = lease_contract.rent_per_year

		if lease_contract.landlord_new:
			payment_recipient, iban = frappe.db.get_value(
				"Landlord", lease_contract.landlord_new, ["landlord_name", "iban"]
			)
		else:
			payment_recipient = ""
			iban = ""

		yield {
			"lease_contract": lease_contract.name,
			"water_body": lease_contract.water_body,
			"water_body_title": lease_contract.water_body_title,
			"fishing_area": lease_contract.fishing_area,
			"lease_object": lease_contract.lease_object,
			"payment_recipient": payment_recipient,
			"iban": iban,
			"rent": rent,
			"currency": lease_contract.currency,
			"payment_reference": lease_contract.payment_reference,
			"payment_type": _(lease_contract.payment_type),
			"payment_due_date": lease_contract.payment_due_date.replace(year=year)
			if lease_contract.payment_due_date
			else None,
		}
