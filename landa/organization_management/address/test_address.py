import frappe
from frappe.tests.utils import FrappeTestCase
from landa.organization_management.address.address import autoname

test_dependencies = ["Organization"]


class TestAddress(FrappeTestCase):
	def test_autoname(self):
		org_name, org_title = frappe.db.get_value(
			"Organization", {}, ("name", "organization_name")
		)
		address = frappe.new_doc("Address")
		address.address_type = "Office"
		address.address_line1 = "Test"
		address.pincode = "04109"
		address.city = "Leipzig"
		address.country = "Germany"
		address.organization = org_name
		address.is_organization_address = 1
		autoname(address, None)

		self.assertIn(f"{org_title} - {org_name}", address.name)
