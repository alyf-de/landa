import frappe
from frappe import _
from frappe.tests.utils import FrappeTestCase

from landa.organization_management.report.magazine_address_list.magazine_address_list import (
	execute,
)

test_dependencies = ["Organization"]


class TestMagazineAddressList(FrappeTestCase):
	def test_column_alignment_for_member_and_external_contact(self):
		last_name = "MagazineAddressListSchema"
		company_name = "Schema Test Institution"
		organization = frappe.db.get_value("Organization", {"is_group": 0}, "name")
		self.assertTrue(organization)

		member = frappe.get_doc(
			{
				"doctype": "LANDA Member",
				"first_name": "MemberFirst",
				"last_name": last_name,
				"organization": organization,
				"magazine_recipient": 1,
			}
		).insert()
		create_address("Member Way 1", "LANDA Member", member.name)

		external_contact = frappe.get_doc(
			{
				"doctype": "External Contact",
				"first_name": "ContactFirst",
				"last_name": last_name,
				"organization": organization,
				"external_organization_name": company_name,
				"is_magazine_recipient": 1,
			}
		).insert()
		create_address("Contact Way 9", "External Contact", external_contact.name)

		columns, data = execute({"last_name": last_name, "only_active_magazine": 0})
		fieldnames = [column["fieldname"] for column in columns]
		self.assertIn("external_organization_name", fieldnames)

		rows = [dict(zip(fieldnames, row, strict=True)) for row in data]
		self.assertEqual(len(rows), 2)

		member_row = next(row for row in rows if row["landa_member"] == member.name)
		self.assertEqual(member_row["first_name"], "MemberFirst")
		self.assertEqual(member_row["last_name"], last_name)
		self.assertEqual(member_row["external_organization_name"], "")
		self.assertEqual(member_row["organization"], organization)
		self.assertEqual(member_row["address_line1"], "Member Way 1")

		contact_row = next(row for row in rows if row["landa_member"] == "")
		self.assertEqual(contact_row["first_name"], "ContactFirst")
		self.assertEqual(contact_row["last_name"], last_name)
		self.assertEqual(contact_row["external_organization_name"], company_name)
		self.assertEqual(contact_row["organization"], organization)
		self.assertEqual(contact_row["organization_name"], _("External Contact"))
		self.assertEqual(contact_row["address_line1"], "Contact Way 9")


def create_address(address_line1, link_doctype, link_name):
	frappe.get_doc(
		{
			"doctype": "Address",
			"address_type": "Personal",
			"address_line1": address_line1,
			"pincode": "01067",
			"city": "Dresden",
			"country": "Germany",
			"links": [{"link_doctype": link_doctype, "link_name": link_name}],
		}
	).insert()
