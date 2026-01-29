# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

from datetime import date

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
	"""Yield report rows for the selected year and filters.

	We query lease contracts joined with their rent periods up to year_end. End dates
	may be unset, so we do not filter by end_date/to_date in the query. If they are
	set and end before year_start, we skip those rows.

	Each rent period returned by the join becomes one report row. The rent amount is
	prorated to the report year by get_prorated_rent.
	"""
	year_end = getdate(f"{year}-12-31")
	year_start = getdate(f"{year}-01-01")
	filters = [
		["start_date", "<=", year_end],
		["Lease Contract Rent", "from_date", "<=", year_end],
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
			"end_date",
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
		if lease_contract.end_date and lease_contract.end_date < year_start:
			# Contract ended before the year start, skip it
			continue

		if lease_contract.to_date and lease_contract.to_date < year_start:
			# Rent period ended before the year start, skip it
			continue

		yield get_rent_payment_row(lease_contract, year_start, year_end)


def get_rent_payment_row(lease_contract: dict, year_start: date, year_end: date) -> dict:
	"""Build a report row for a single rent period.

	Looks up landlord details, prorates the rent for the report year, and aligns
	the payment due date to the report year.
	"""
	if lease_contract.landlord_new:
		payment_recipient, iban = frappe.db.get_value(
			"Landlord", lease_contract.landlord_new, ["landlord_name", "iban"]
		)
	else:
		payment_recipient = ""
		iban = ""

	return {
		"lease_contract": lease_contract.name,
		"water_body": lease_contract.water_body,
		"water_body_title": lease_contract.water_body_title,
		"fishing_area": lease_contract.fishing_area,
		"lease_object": lease_contract.lease_object,
		"payment_recipient": payment_recipient,
		"iban": iban,
		"rent": get_prorated_rent(
			year_start=year_start,
			year_end=year_end,
			rent_per_year=lease_contract.rent_per_year,
			from_date=lease_contract.from_date,
			to_date=lease_contract.to_date,
		),
		"currency": lease_contract.currency,
		"payment_reference": lease_contract.payment_reference,
		"payment_type": _(lease_contract.payment_type),
		"payment_due_date": change_year(lease_contract.payment_due_date, year_start.year)
		if lease_contract.payment_due_date
		else None,
	}


def get_prorated_rent(
	year_start: date,
	year_end: date,
	rent_per_year: float,
	from_date: date | None = None,
	to_date: date | None = None,
) -> float:
	"""Return the rent amount for the report year for a single rent period.

	If the rent period does not cover the full year, prorate by the fraction of
	days within the year (using actual day counts, so leap years are handled).
	Open-ended from/to dates are treated as the year boundaries.

	Example (report year 2026):
	    Inputs -> output (rent amount for 2026):
	        - rent_per_year=500, from_date=2024-01-01, to_date=2024-12-31 -> skipped
	        - rent_per_year=1000, from_date=2025-01-01, to_date=2026-06-30 -> 500
	        - rent_per_year=1500, from_date=2026-07-01, to_date=2027-12-31 -> 750
	    Invalid inputs:
	        - to_date < year_start are filtered before this function is called.
	"""

	# Check if we need to calculate partial rent
	# Only calculate partial rent if the contract period doesn't fully cover the year
	contract_start_in_year = max(year_start, from_date) if from_date else year_start
	contract_end_in_year = min(year_end, to_date) if to_date else year_end

	if (from_date and from_date > year_start) or (to_date and to_date < year_end):
		# Calculate partial rent using actual days in the year (handles leap years)
		days_in_contract_period = (contract_end_in_year - contract_start_in_year).days + 1
		days_in_year = (year_end - year_start).days + 1

		return round(
			rent_per_year * round(days_in_contract_period / days_in_year, 2),
			2,
		)
	else:
		return rent_per_year


def change_year(date_to_change: date | None, new_year: int) -> date | None:
	"""Change the year of a date.

	Args:
	    date_to_change: The date to change the year of.
	    new_year: The new year to set.

	Returns:
	    The date with the new year.
	"""
	if date_to_change is None:
		return None

	try:
		return date_to_change.replace(year=new_year)
	except ValueError:
		# This can happen in two main scenarios:
		# 1. Leap year issue: Feb 29 in a non-leap year (most common)
		# 2. Invalid year value (outside 1-9999 range)
		if date_to_change.month == 2 and date_to_change.day == 29:
			# Handle leap year case: move Feb 29 to Feb 28 in non-leap years
			return date_to_change.replace(year=new_year, day=28)
		else:
			# For other ValueError cases (like invalid year), re-raise the exception
			# since we can't safely handle those
			raise
