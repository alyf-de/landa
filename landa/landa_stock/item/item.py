import frappe


def before_insert(item, event):
	if not frappe.flags.in_migrate:
		set_year_of_validity(item)
		set_tax_template(item)


def set_year_of_validity(item):
	"""Set "Valid From Year" and "Valid To Year" to year_of_validity from Attribute Value."""
	if item.variant_of and item.attributes:
		years = [row.attribute_value for row in item.attributes if row.attribute == 'Gültigkeitsjahr']
		if years:
			year = years[0]
			item.valid_from_year = year
			item.valid_to_year = year
	

def set_tax_template(item):
	if item.item_tax_template:
		item.append('taxes', {
			'item_tax_template': item.item_tax_template,
		})


def autoname(item, event):
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
