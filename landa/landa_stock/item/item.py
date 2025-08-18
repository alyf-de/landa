from typing import TYPE_CHECKING

import frappe

if TYPE_CHECKING:
	from erpnext.stock.doctype.item.item import Item


def before_validate(item: "Item", event):
	if frappe.flags.in_migrate:
		return

	set_item_defaults(item)


def before_insert(item: "Item", event):
	if frappe.flags.in_migrate:
		return

	set_year_of_validity(item)
	set_tax_template(item)


def set_year_of_validity(item: "Item"):
	"""Set "Valid From Year" and "Valid To Year" to year_of_validity from Attribute Value."""
	if item.variant_of and item.attributes:
		years = [row.attribute_value for row in item.attributes if row.attribute == "Gültigkeitsjahr"]
		if years:
			year = years[0]
			item.valid_from_year = year
			item.valid_to_year = year


def set_tax_template(item: "Item"):
	if item.item_tax_template:
		item.append(
			"taxes",
			{
				"item_tax_template": item.item_tax_template,
			},
		)


def autoname(item: "Item", event):
	"""Create Company-specific Item name."""
	if item.variant_of:
		# Variant uses the Company-specific name of the template Item together
		# with a list of Item Attribute Values.
		# For example, `ART-AVL-0001-SALMON-2020`
		if not item.item_code:
			from erpnext.controllers.item_variant import make_variant_item_code

			template_item_name = frappe.db.get_value("Item", item.variant_of, "item_name")
			make_variant_item_code(item.variant_of, template_item_name, item)
	else:
		# Normal Items get named like `ART-{company_abbr}-####`
		# For example, `ART-AVL-0001`
		from frappe.model.naming import make_autoname

		series = "A-"
		if item.company:
			series += frappe.get_value("Company", item.company, "abbr") + "-"

		item.name = make_autoname(f"{series}.####", "Item")
		item.item_code = item.name


def set_item_defaults(item: "Item"):
	"""Set Item Defaults with the company-specific price list."""
	if not item.company:
		return

	if len(item.item_defaults) == 1 and item.item_defaults[0].company == item.company:
		return

	item.item_defaults = []
	item.append(
		"item_defaults",
		{
			"company": item.company,
			"default_price_list": frappe.db.get_value(
				"Price List", {"company": item.company, "selling": 1, "enabled": 1}
			),
		},
	)
