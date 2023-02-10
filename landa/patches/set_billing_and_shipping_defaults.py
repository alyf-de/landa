import json
import os

import frappe
from frappe.modules.utils import sync_customizations_for_doctype
from frappe.query_builder import DocType


def execute():
	set_billing_and_shipping_defaults()
	# Cleanup of data not yet now, but in the next release. Ask Samuel why.
	# TODO: Clean data
	# cleanup_addresses()
	# cleanup_contacts()


def customize_customer():
	folder = frappe.get_app_path("landa", "landa_sales", "custom")
	fname = "customer.json"

	with open(os.path.join(folder, fname), "r") as f:
		sync_customizations_for_doctype(json.loads(f.read()), folder)


def set_billing_and_shipping_defaults():
	customize_customer()

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

	for address_name, is_shipping, is_primary, customer in addresses:
		if is_primary:  # billing address
			contact = frappe.get_all(
				"Contact",
				[["name", "like", address_name.replace(" ", "%")]],
				pluck="name",
			)

			frappe.db.set_value(
				"Customer",
				customer,
				{
					"default_billing_contact": contact[0] if contact else None,
					"default_billing_address": address_name,
				},
			)

		if is_shipping:
			contact = frappe.get_all(
				"Contact",
				[["name", "like", address_name.replace(" ", "%")]],
				pluck="name",
			)

			frappe.db.set_value(
				"Customer",
				customer,
				{
					"default_shipping_contact": contact[0] if contact else None,
					"default_shipping_address": address_name,
				},
			)


def cleanup_addresses():
	# the two checkboxes are no longer used and are hidden from now on.
	frappe.db.sql(
		"""update `tabAddress` set is_shipping_address=0, is_primary_address=0"""
	)

def cleanup_contacts():
	# the two checkboxes are no longer used and are hidden from now on.
	frappe.db.sql(
		"""update `tabContact` set is_billing_contact=0, is_primary_contact=0"""
	)
