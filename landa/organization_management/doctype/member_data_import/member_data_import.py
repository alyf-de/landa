# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.dateutils import parse_date
from landa.organization_management.doctype.landa_member.landa_member import LANDAMember
from datetime import datetime


class MemberDataImport(Document):

	MEMBER_FIELDS = [
		"first_name",
		"last_name",
		"date_of_birth",
		"is_supporting_member",
		"has_key",
		"has_special_yearly_fishing_permit_1",
		"has_special_yearly_fishing_permit_2",
		"youth_membership",
		"additional_information",
	]

	ADDRESS_FIELDS = ["address_line1", "pincode", "city"]

	def before_insert(self):
		self.preprocess()

	def db_insert(self):
		self.create_or_update_member()
		self.create_or_update_address()
		self.create_permit()
		return {}

	def load_from_db(self):
		pass

	def db_update(self):
		pass

	def get_list(self, _args=None) -> list:
		return []

	def get_count(self, _args=None) -> int:
		return 0

	def get_stats(self, _args=None) -> dict:
		return {"stats": {}}

	def preprocess(self):
		"""Remove whitespaces, parse checkbox values and dates."""
		for field in self.meta.fields:
			value = self.get(field.fieldname)
			if not isinstance(value, str):
				continue

			if field.fieldtype in ("Data", "Link"):
				self.set(field.fieldname, value.strip())
			elif field.fieldtype == "Check":
				self.set(field.fieldname, parse_checkbox_value(value))
			elif field.fieldtype == "Date":
				if not value:
					continue
				self.set(field.fieldname, parse_date(value))
			elif field.fieldtype == "Int":
				self.set(field.fieldname, int(value))

	def create_or_update_member(self):
		if self.member:
			member_doc = frappe.get_doc("LANDA Member", self.member)
		elif self.organization and self.last_name:
			member_doc = create_member(self.organization, self.last_name)
			self.member = member_doc.name
		else:
			frappe.throw(
				'Es müssen entweder die Felder "Familienname" und "Verein" ausgefüllt sein, um ein neues Mitglied zu erstellen oder es muss eine Mitgliedsnummer angegeben werden, um die Daten eines bestehenden Mitglieds zu bearbeiten.'
			)

		self.update_doc(member_doc, self.MEMBER_FIELDS)

	def create_or_update_address(self):
		if self.address_name:
			address_doc = frappe.get_doc("Address", self.address_name)
			self.update_doc(address_doc, self.ADDRESS_FIELDS)
		elif all(
			[
				self.address_line1,
				self.pincode,
				self.city,
				self.member,
				self.organization,
			]
		):
			create_address(
				address_line1=self.address_line1,
				pincode=self.pincode,
				city=self.city,
				member=self.member,
				organization=self.organization,
			)

	def create_permit(self):
		if self.yearly_fishing_permit or not all(
			[self.year, self.number, self.member, self.organization]
		):
			# permit exists or required fields are missing
			return

		doctype = "Yearly Fishing Permit Type"
		if not self.type or not frappe.db.exists(doctype, self.type):
			default_type = "ALLG"
			if frappe.db.exists(doctype, default_type):
				self.type = default_type
			else:
				return

		if not self.date_of_issue:
			self.date_of_issue = datetime.now().date()

		create_yearly_fishing_permit(
			member=self.member,
			year=self.year,
			type=self.type,
			number=self.number,
			date_of_issue=self.date_of_issue,
			organization=self.organization,
		)

	def update_doc(self, doc: Document, fields: "list[str]"):
		"""Update all `fields` of `doc` with the values from `self`."""
		for fieldname in fields:
			new_value = self.get(fieldname)
			if not new_value and not isinstance(
				new_value, int
			):	# int == 0 is allowed to disable checkbox
				continue

			old_value = doc.get(fieldname)
			fieldtype = doc.meta.get_field(fieldname).fieldtype

			if fieldtype == "Date":
				# For some reason `new_value` is of type `datetime`.
				# `old_value` is of type `date` as expected.
				if isinstance(new_value, datetime):
					new_value = new_value.date()

			elif fieldtype == "Data":
				old_value = (old_value or "").strip()

			if old_value != new_value:
				doc.set(fieldname, new_value)

		doc.save()


def create_member(organization: str, last_name: str) -> LANDAMember:
	"""Return a new LANDA Member."""
	member = frappe.new_doc("LANDA Member")
	member.organization = organization
	member.last_name = last_name

	return member.insert()


def create_address(
	address_line1: str, pincode: str, city: str, member: str, organization: str
) -> None:
	"""Return a new Address linked to LANDA Member."""
	address = frappe.new_doc("Address")
	address.address_type = "Personal"
	address.address_line1 = address_line1
	address.pincode = pincode
	address.city = city
	address.country = "Germany"
	address.is_primary_address = 1
	address.is_shipping_address = 1
	address.append("links", {"link_doctype": "LANDA Member", "link_name": member})
	address.organization = organization

	address.insert()


def create_yearly_fishing_permit(
	member: str, year: int, type: str, number: str, date_of_issue, organization: str
) -> None:
	data = {"member": member, "year": year, "type": type, "organization": organization}

	if frappe.db.exists("Yearly Fishing Permit", data):
		return

	yfp = frappe.new_doc("Yearly Fishing Permit")
	yfp.update(data)
	yfp.number = number
	yfp.date_of_issue = date_of_issue
	yfp.insert()


def parse_checkbox_value(value: str) -> int:
	scrubbed = value.strip().lower()

	if scrubbed in ["1", "ja", "j", "yes", "y"]:
		return 1
	else:
		return 0
