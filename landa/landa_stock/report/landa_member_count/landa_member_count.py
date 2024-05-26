# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika.functions import Cast, Sum
from pypika.terms import Case, PseudoColumn


def get_data(
	organization: str,
	year: str = None,
	company: str = None,
	company_abbr: str = None,
	show_total_for_regional_org: bool = False,
):
	DeliveryNoteItem = frappe.qb.DocType("Delivery Note Item")
	DeliveryNote = frappe.qb.DocType("Delivery Note")
	Item = frappe.qb.DocType("Item")
	ItemVariantAttribute = frappe.qb.DocType("Item Variant Attribute")
	Organization = frappe.qb.DocType("Organization")

	query = (
		frappe.qb.from_(DeliveryNoteItem)
		.join(Item)
		.on(Item.item_code == DeliveryNoteItem.item_code)
		.join(ItemVariantAttribute)
		.on(ItemVariantAttribute.parent == DeliveryNoteItem.item_code)
		.join(DeliveryNote)
		.on(DeliveryNote.name == DeliveryNoteItem.parent)
		.join(Organization)
		.on(Organization.name == DeliveryNote.organization)
	)

	if show_total_for_regional_org:
		query = query.select(
			PseudoColumn(f"'{company_abbr}'"),
			DeliveryNote.company,
		)
	else:
		query = query.select(
			DeliveryNote.customer,
			DeliveryNote.customer_name,
		)
	query = query.select(
		Cast(DeliveryNote.year_of_settlement, "CHAR(4)"),
		Sum(
			Case()
			.when(
				ItemVariantAttribute.attribute_value == "Vollzahler",
				DeliveryNoteItem.qty,
			)
			.else_(0)
		),
		Sum(
			Case()
			.when(
				ItemVariantAttribute.attribute_value == "Jugend",
				DeliveryNoteItem.qty,
			)
			.else_(0)
		),
		Sum(
			Case()
			.when(
				ItemVariantAttribute.attribute_value == "Fördermitglied",
				DeliveryNoteItem.qty,
			)
			.else_(0)
		),
		Sum(
			Case()
			.when(
				ItemVariantAttribute.attribute_value.isin(["Vollzahler", "Jugend", "Fördermitglied"]),
				DeliveryNoteItem.qty,
			)
			.else_(0)
		),
	).where(
		(ItemVariantAttribute.attribute == "Beitragsart")
		& (DeliveryNote.docstatus == 1)
		& DeliveryNote.organization.like(f"{organization}%")
	)

	if year:
		query = query.where(DeliveryNote.year_of_settlement == year)

	if company:
		query = query.where(DeliveryNote.company == company)

	query = query.groupby(DeliveryNote.year_of_settlement)

	if show_total_for_regional_org:
		query = query.groupby(DeliveryNote.company)
	else:
		query = query.groupby(DeliveryNote.customer)

	query = query.orderby(DeliveryNote.customer, DeliveryNote.year_of_settlement)
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
			"fieldname": "gesamt",
			"fieldtype": "Data",
			"label": _("Gesamt"),
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
