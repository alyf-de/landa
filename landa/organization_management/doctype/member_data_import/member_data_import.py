# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.dateutils import parse_date


class MemberDataImport(Document):

	DATA_FIELDS = [
		"member",
		"last_name",
		"first_name",
		"address",
		"address_line1",
		"pincode",
		"city",
		"organization",
		"year",
		"type",
		"number",
		"additional_information",
	]

	CHECK_FIELDS = [
		"is_supporting_member",
		"has_key",
		"has_special_yearly_fishing_permit_1",
		"has_special_yearly_fishing_permit_2",
	]

	DATE_FIELDS = ["date_of_birth", "date_of_issue"]

	MEMBER_FIELDS = [
		"first_name",
		"last_name",
		"date_of_birth",
		"is_supporting_member",
		"has_key",
		"has_special_yearly_fishing_permit_1",
		"has_special_yearly_fishing_permit_2",
	]

	ADDRESS_FIELDS = ["address_line1", "pincode", "city"]

	def get(self, fieldname):
		return super(MemberDataImport, self).get(fieldname) or ""

	def db_insert(self):
		self.preprocess()
		self.process_member()
		self.process_address()
		self.process_fishing_permit()

	def load_from_db(self):
		pass

	def db_update(self):
		pass

	def get_list(self, args):
		return []

	def preprocess(self):
		"""Remove whitespaces, parse checkbox values and dates."""
		for field in self.DATA_FIELDS:
			self.set(field, self.get(field).strip())

		for field in self.CHECK_FIELDS:
			scrubbed = self.get(field).strip().lower()
			if scrubbed in ["1", "ja", "j", "yes"]:
				self.set(field, 1)
			elif scrubbed in ["0", "nein", "n", "no", "-"]:
				self.set(field, 0)
			else:
				self.set(field, None)

		for field in self.DATE_FIELDS:
			if not self.get(field):
				continue

			self.set(field, parse_date(self.get(field)))

	def process_member(self):
		if self.member:
			member_doc = frappe.get_doc("LANDA Member", self.member)
		elif self.organization and self.last_name:
			member_doc = self.create_member()
			self.member = member_doc.name
		else:
			frappe.throw(
				'Es müssen entweder die Felder "Familienname" und "Verein" ausgefüllt sein, um ein neues Mitglied zu erstellen oder es muss eine Mitgliedsnummer angegeben werden, um die Daten eines bestehenden Mitglieds zu bearbeiten.'
			)

		self.update_doc(member_doc, self.MEMBER_FIELDS)

	def process_address(self):
		if self.address_name:
			address_doc = frappe.get_doc("Address", self.address_name)
			self.update_doc(address_doc, self.ADDRESS_FIELDS)
		elif all([self.address_line1, self.pincode, self.city]):
			self.create_address()

	def process_fishing_permit(self):
		if not self.year:
			return

		doctype = "Yearly Fishing Permit Type"
		default_type = "ALLG"
		if (not self.type or not frappe.db.exists(doctype, self.type)):
			if frappe.db.exists(doctype, default_type):
				self.type = default_type
			else:
				return

		self.create_yearly_fishing_permit()

	def create_member(self):
		"""Return a new LANDA Member."""
		member = frappe.new_doc("LANDA Member")
		member.organization = self.organization
		member.last_name = self.last_name

		return member.insert()

	def update_doc(self, doc, fields):
		"""Update all `fields` of `doc` with the values from `self`."""
		for field in fields:
			new_value = self.get(field)
			if not new_value and not type(new_value, int): # int == 0 is allowed to disable checkbox
				continue

			old_value = doc.get(field)
			if field in self.DATE_FIELDS:
				old_value = old_value.isoformat() if old_value else ""
			elif field in self.DATA_FIELDS:
				old_value = (old_value or "").strip()

			if old_value != new_value:
				doc.set(field, new_value)

		doc.save()

	def create_address(self):
		"""Return a new Address linked to LANDA Member."""
		address = frappe.new_doc("Address")
		address.address_type = "Personal"
		address.address_line1 = self.address_line1
		address.pincode = self.pincode
		address.city = self.city
		address.country = "Germany"
		address.is_primary_address = 1
		address.is_shipping_address = 1
		address.append(
			"links", {"link_doctype": "LANDA Member", "link_name": self.member}
		)

		return address.insert()

	def create_yearly_fishing_permit(self):
		yfp = frappe.new_doc("Yearly Fishing Permit")
		yfp.member = self.member
		yfp.year = int(self.year)
		yfp.type = self.type.upper()
		yfp.number = self.number
		yfp.date_of_issue = self.date_of_issue

		yfp.insert()
		yfp.submit()
		return yfp
