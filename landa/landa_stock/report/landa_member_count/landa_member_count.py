# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika.functions import Cast, Sum
from pypika.terms import Case, PseudoColumn


def get_data(
	organization: str = None,
	year: str = None,
	company: str = None,
	company_abbr: str = None,
	show_total_for_regional_org: bool = False,
):
	delivery_note_item = frappe.qb.DocType("Delivery Note Item")
	delivery_note = frappe.qb.DocType("Delivery Note")
	item = frappe.qb.DocType("Item")
	item_variant_attribute = frappe.qb.DocType("Item Variant Attribute")

	query = (
		frappe.qb.from_(delivery_note_item)
		.join(item)
		.on(item.item_code == delivery_note_item.item_code)
		.join(item_variant_attribute)
		.on(item_variant_attribute.parent == delivery_note_item.item_code)
		.join(delivery_note)
		.on(delivery_note.name == delivery_note_item.parent)
	)

	if show_total_for_regional_org:
		query = query.select(
			PseudoColumn(f"'{company_abbr}'"),
			delivery_note.company,
		)
	else:
		query = query.select(
			delivery_note.customer,
			delivery_note.customer_name,
		)
	query = query.select(
		Cast(delivery_note.year_of_settlement, "CHAR(4)"),
		Sum(
			Case()
			.when(
				item_variant_attribute.attribute_value == "Vollzahler",
				delivery_note_item.qty,
			)
			.else_(0)
		),
		Sum(
			Case()
			.when(
				item_variant_attribute.attribute_value == "Jugend",
				delivery_note_item.qty,
			)
			.else_(0)
		),
		Sum(
			Case()
			.when(
				item_variant_attribute.attribute_value == "Fördermitglied",
				delivery_note_item.qty,
			)
			.else_(0)
		),
		Sum(
			Case()
			.when(
				item_variant_attribute.attribute_value == "Austauschmarke",
				delivery_note_item.qty,
			)
			.else_(0)
		),
	).where((item_variant_attribute.attribute == "Beitragsart") & (delivery_note.docstatus == 1))

	if year:
		query = query.where(delivery_note.year_of_settlement == year)

	if organization:
		query = query.where(delivery_note.organization.like(f"{organization}%"))

	if company:
		query = query.where(delivery_note.company == company)

	query = query.groupby(delivery_note.year_of_settlement)

	if show_total_for_regional_org:
		query = query.groupby(delivery_note.company)
	else:
		query = query.groupby(delivery_note.customer)

	query = query.orderby(delivery_note.customer, delivery_note.year_of_settlement)
	return query.run()


def get_columns():
	return [
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"label": _("Organization"),
			"options": "Organization",
			"width": 150,
		},
		{
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"label": _("Organization Name"),
			"width": 250,
		},
		{
			"fieldname": "year",
			"fieldtype": "Data",
			"label": _("Year"),
			"width": 150,
		},
		{
			"fieldname": "vollzahler",
			"fieldtype": "Data",
			"label": _("Vollzahler"),
			"width": 150,
		},
		{
			"fieldname": "jugend",
			"fieldtype": "Data",
			"label": _("Jugend"),
			"width": 150,
		},
		{
			"fieldname": "foerdermitglied",
			"fieldtype": "Data",
			"label": _("Fördermitglied"),
			"width": 150,
		},
		{
			"fieldname": "austauschmarke",
			"fieldtype": "Data",
			"label": _("Austauschmarke"),
			"width": 150,
		},
	]


def execute(filters=None):
	organization = filters.pop("organization", None)
	total = filters.pop("total", 0)
	company = None
	company_abbr = None

	if organization and organization in ["AVL", "AVS", "AVE"]:
		company = frappe.get_value("Organization", organization, "organization_name")
		company_abbr = organization
	else:
		total = 0

	if company or "organization" in filters:
		return get_columns(), get_data(
			organization,
			filters.get("year"),
			company,
			company_abbr,
			total == 1,
		)
	else:
		return [], []
