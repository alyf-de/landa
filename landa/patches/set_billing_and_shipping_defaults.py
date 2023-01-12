import frappe
from frappe.query_builder import DocType


def execute():
	set_billing_and_shipping_defaults()
	cleanup_addresses()


def set_billing_and_shipping_defaults():
	Address = DocType("Address")
	DynamicLink = DocType("Dynamic Link")

	addresses = (
		frappe.qb.from_(Address)
		.inner_join(DynamicLink)
		.on(Address.name == DynamicLink.parent)
		.select(
			Address.name,
			Address.is_shipping_address,
			Address.is_primary_address,
			DynamicLink.link_name,
		)
		.where((Address.is_shipping_address == 1) | (Address.is_primary_address == 1))
		.where(DynamicLink.link_doctype == "Customer")
		.run()
	)

	for addr in addresses:
		if addr[2]:  # is_primary_address (billing address)
			contact = frappe.get_all(
				"Contact", [["name", "like", addr[0].replace(" ", "%")]], pluck="name"
			)

			frappe.db.set_value(
				"Customer",
				addr[3],
				{
					"default_billing_contact": contact[0] if contact else None,
					"default_billing_address": addr[0],
				},
			)

		if addr[1]:  # is_shipping_address
			contact = frappe.get_all(
				"Contact", [["name", "like", addr[0].replace(" ", "%")]], pluck="name"
			)

			frappe.db.set_value(
				"Customer",
				addr[3],
				{
					"default_shipping_contact": contact[0] if contact else None,
					"default_shipping_address": addr[0],
				},
			)


def cleanup_addresses():
	# the two checkboxes are no longer used and are hidden from now on.
	frappe.db.sql(
		"""update `tabAddress` set is_shipping_address=0, is_primary_address=0"""
	)
