# Copyright (c) 2021, Real Experts GmbH and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from landa.organization_management.doctype.organization.organization import (
	create_customer,
	get_single_address_and_contact,
	member_with_address_and_contact_query,
)


class TestOrganization(FrappeTestCase):
	def test_autoname(self):
		orgs = frappe.get_all("Organization", pluck="name")

		self.assertIn("ST", orgs)
		self.assertIn("REG", orgs)
		self.assertIn("REG-001", orgs)
		self.assertIn("REG-002", orgs)
		self.assertIn("REG-002-01", orgs)

	def test_company_and_customer_exist(self):
		self.assertTrue(frappe.db.exists("Company", {"abbr": "REG"}))
		self.assertTrue(frappe.db.exists("Customer", "REG-001"))
		self.assertTrue(frappe.db.exists("Customer", "REG-002"))

	def test_customer_gets_price_list_of_company(self):
		# ERPNext sets the root group as default for tests, but a customer needs a leaf group
		self.addCleanup(frappe.db.set_default, "customer_group", frappe.db.get_default("customer_group"))
		frappe.db.set_default("customer_group", "Non Profit")

		company = frappe.db.get_value("Company", {"abbr": "REG"})
		price_list = frappe.get_doc(
			{
				"doctype": "Price List",
				"price_list_name": "Standard - REG",
				"currency": "EUR",
				"selling": 1,
				"company": company,
			}
		).insert()
		organization = frappe.get_doc(
			{
				"doctype": "Organization",
				"organization_name": "Local Organization with Price List",
				"parent_organization": "REG",
			}
		).insert()

		create_customer(organization.name, organization.organization_name)

		self.assertEqual(
			frappe.db.get_value("Customer", organization.name, "default_price_list"), price_list.name
		)

	def test_member_query_returns_members_with_an_address_and_contact(self):
		organization = insert_local_organization("Linkable Members")
		other_organization = insert_local_organization("Other Linkable Members")

		one_of_each = insert_member(organization.name, "Able One")
		link_contact(one_of_each.name)
		link_address(one_of_each.name, "Able Way 1")

		enabled_and_disabled = insert_member(organization.name, "Able Two")
		link_contact(enabled_and_disabled.name)
		link_address(enabled_and_disabled.name, "Able Way 2")
		link_address(enabled_and_disabled.name, "Able Way 2 disabled", disabled=1)

		two_addresses = insert_member(organization.name, "Baker Two Addresses")
		link_contact(two_addresses.name)
		link_address(two_addresses.name, "Baker Way 1")
		link_address(two_addresses.name, "Baker Way 2")

		no_address = insert_member(organization.name, "Carter No Address")
		link_contact(no_address.name)

		two_contacts = insert_member(organization.name, "Dunn Two Contacts")
		link_contact(two_contacts.name, "One")
		link_contact(two_contacts.name, "Two")
		link_address(two_contacts.name, "Dunn Way 1")

		no_contact = insert_member(organization.name, "Ellis No Contact")
		link_address(no_contact.name, "Ellis Way 1")

		disabled_address = insert_member(organization.name, "Frost Disabled Address")
		link_contact(disabled_address.name)
		link_address(disabled_address.name, "Frost Way 1", disabled=1)

		other_org_member = insert_member(other_organization.name, "Able Zero")
		link_contact(other_org_member.name)
		link_address(other_org_member.name, "Zero Way 1")

		rows = member_query(organization.name)
		self.assertEqual(
			[row[0] for row in rows],
			[one_of_each.name, enabled_and_disabled.name, two_addresses.name, two_contacts.name],
		)
		self.assertEqual(rows[0][1], "Able One")

		self.assertEqual(
			[row[0] for row in member_query(organization.name, txt="Able")],
			[one_of_each.name, enabled_and_disabled.name],
		)
		self.assertEqual(
			[row[0] for row in member_query(organization.name, txt="Baker")], [two_addresses.name]
		)
		self.assertEqual(member_query(organization.name, txt="Zero"), [])
		self.assertEqual(member_query(None), [])

	def test_get_single_address_and_contact(self):
		organization = insert_local_organization("Single Address And Contact")
		one = insert_member(organization.name, "Single")
		contact = link_contact(one.name, "Only")
		address = link_address(one.name, "Single Way")
		self.assertEqual(
			get_single_address_and_contact(one.name),
			{"contact": contact.name, "address": address.name},
		)

		several = insert_member(organization.name, "Several")
		link_contact(several.name, "One")
		link_contact(several.name, "Two")
		several_address = link_address(several.name, "Several Way")
		self.assertEqual(
			get_single_address_and_contact(several.name),
			{"contact": None, "address": several_address.name},
		)

	def test_link_contact_links_the_selected_records(self):
		self.addCleanup(frappe.db.set_default, "customer_group", frappe.db.get_default("customer_group"))
		frappe.db.set_default("customer_group", "Non Profit")

		organization = insert_local_organization("Link Selected Contact")
		create_customer(organization.name, organization.organization_name)
		member = insert_member(organization.name, "Selected")
		first = link_contact(member.name, "First")
		second = link_contact(member.name, "Second")
		address = link_address(member.name, "Selected Way")

		organization.link_contact(member.name, second.name, address.name, is_default_billing=1)

		self.assertTrue(has_link(second.name, "Contact", "Organization", organization.name))
		self.assertTrue(has_link(second.name, "Contact", "Customer", organization.name))
		self.assertTrue(has_link(address.name, "Address", "Organization", organization.name))
		self.assertFalse(has_link(first.name, "Contact", "Organization", organization.name))

		customer = frappe.get_doc("Customer", organization.name)
		self.assertEqual(customer.default_billing_contact, second.name)
		self.assertEqual(customer.default_billing_address, address.name)

	def test_link_contact_rejects_records_that_do_not_belong_to_the_member(self):
		organization = insert_local_organization("Reject Other Contact")
		other_organization = insert_local_organization("Reject Other Organization")
		member = insert_member(organization.name, "Owner")
		other_member = insert_member(organization.name, "Other")
		outside_member = insert_member(other_organization.name, "Outside")
		contact = link_contact(member.name)
		other_contact = link_contact(other_member.name)
		address = link_address(member.name, "Owner Way")
		disabled_address = link_address(member.name, "Owner Way Disabled", disabled=1)

		self.assertRaises(
			frappe.ValidationError,
			organization.link_contact,
			member.name,
			other_contact.name,
			address.name,
		)
		self.assertRaises(
			frappe.ValidationError,
			organization.link_contact,
			member.name,
			contact.name,
			disabled_address.name,
		)
		self.assertRaises(
			frappe.ValidationError,
			organization.link_contact,
			outside_member.name,
			contact.name,
			address.name,
		)


def insert_local_organization(organization_name: str):
	return frappe.get_doc(
		{
			"doctype": "Organization",
			"organization_name": organization_name,
			"parent_organization": "REG",
		}
	).insert()


def insert_member(organization: str, last_name: str):
	return frappe.get_doc(
		{
			"doctype": "LANDA Member",
			"organization": organization,
			"last_name": last_name,
		}
	).insert()


def link_contact(member: str, first_name: str = "Contact"):
	return frappe.get_doc(
		{
			"doctype": "Contact",
			"first_name": first_name,
			"links": [{"link_doctype": "LANDA Member", "link_name": member}],
		}
	).insert()


def link_address(member: str, address_line1: str, disabled: int = 0):
	address = frappe.get_doc(
		{
			"doctype": "Address",
			"address_title": address_line1,
			"address_type": "Personal",
			"address_line1": address_line1,
			"pincode": "01067",
			"city": "Dresden",
			"country": "Germany",
			"links": [{"link_doctype": "LANDA Member", "link_name": member}],
		}
	)
	address.disabled = disabled
	return address.insert()


def has_link(parent: str, parenttype: str, link_doctype: str, link_name: str) -> bool:
	return bool(
		frappe.db.exists(
			"Dynamic Link",
			{
				"parent": parent,
				"parenttype": parenttype,
				"link_doctype": link_doctype,
				"link_name": link_name,
			},
		)
	)


def member_query(organization: str | None, txt: str = ""):
	return member_with_address_and_contact_query(
		"LANDA Member",
		txt,
		"full_name",
		0,
		20,
		{"organization": organization} if organization else {},
	)
