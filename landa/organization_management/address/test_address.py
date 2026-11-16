import frappe
from frappe.tests.utils import FrappeTestCase

from landa.organization_management.address.address import autoname

test_dependencies = ["Organization"]


class TestAddressAutoname(FrappeTestCase):
	def get_address_title(self, external_contact: dict) -> str:
		contact = frappe.get_doc(
			{"doctype": "External Contact", "organization": "REG", **external_contact}
		).insert()

		address = frappe.new_doc("Address")
		address.append("links", {"link_doctype": "External Contact", "link_name": contact.name})
		autoname(address, None)

		self.assertEqual(address.name, f"{address.address_title} - {contact.name}")
		return address.address_title

	def test_external_contact_with_full_name(self):
		title = self.get_address_title({"first_name": "Jane", "last_name": "Doe"})
		self.assertEqual(title, "Jane Doe")

	def test_external_contact_without_last_name(self):
		title = self.get_address_title({"first_name": "Jane"})
		self.assertEqual(title, "Jane")

	def test_external_contact_without_person_name(self):
		title = self.get_address_title({"external_organization_name": "Acme"})
		self.assertEqual(title, "Acme")
