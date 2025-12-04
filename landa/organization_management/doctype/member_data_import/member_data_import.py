# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.dateutils import parse_date

from landa.organization_management.doctype.landa_member.landa_member import LANDAMember
from landa.utils import get_member_and_organization


class MemberDataImport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		additional_information: DF.Data | None
		address_line1: DF.Data | None
		address_name: DF.Data | None
		city: DF.Data | None
		date_of_birth: DF.Date | None
		first_name: DF.Data | None
		has_key: DF.Check
		has_special_yearly_fishing_permit_1: DF.Check
		has_special_yearly_fishing_permit_2: DF.Check
		has_special_yearly_fishing_permit_3: DF.Check
		has_special_yearly_fishing_permit_4: DF.Check
		has_special_yearly_fishing_permit_5: DF.Check
		has_special_yearly_fishing_permit_6: DF.Check
		has_special_yearly_fishing_permit_7: DF.Check
		is_supporting_member: DF.Check
		last_name: DF.Data | None
		member: DF.Data | None
		organization: DF.Link | None
		pincode: DF.Data | None
		type: DF.Link | None
		year: DF.Int
		yearly_fishing_permit: DF.Link | None
		youth_membership: DF.Check
	# end: auto-generated types
	MEMBER_FIELDS = [
		"first_name",
		"last_name",
		"date_of_birth",
		"is_supporting_member",
		"has_key",
		"has_special_yearly_fishing_permit_1",
		"has_special_yearly_fishing_permit_2",
		"has_special_yearly_fishing_permit_3",
		"has_special_yearly_fishing_permit_4",
		"has_special_yearly_fishing_permit_5",
		"has_special_yearly_fishing_permit_6",
		"has_special_yearly_fishing_permit_7",
		"youth_membership",
		"additional_information",
	]

	ADDRESS_FIELDS = ["address_line1", "pincode", "city"]

	def validate(self):
		if self.address_name and not self.member:
			frappe.throw(_("Please set the corresponding LANDA Member"))

		if self.address_name and not frappe.db.exists(
			"Dynamic Link",
			{
				"link_doctype": "LANDA Member",
				"link_name": self.member,
				"parenttype": "Address",
				"parent": self.address_name,
			},
		):
			frappe.throw(_("The selected address does not belong to the selected LANDA Member"))

		self.validate_existing_permit()

	def before_insert(self, *args, **kwargs):
		self.preprocess()

	def db_insert(self, *args, **kwargs):
		self.create_or_update_member()
		self.create_or_update_address()
		self.create_permit()
		return {}

	def load_from_db(self):
		__, member_organization = get_member_and_organization(frappe.session.user)
		super(Document, self).__init__(
			{
				"name": frappe.generate_hash(length=8),
				"organization": member_organization,
			}
		)

	def db_update(self, *args, **kwargs):
		pass

	@staticmethod
	def get_list(self, *args, **kwargs) -> list:
		return []

	@staticmethod
	def get_count(self, *args, **kwargs) -> int:
		return 0

	@staticmethod
	def get_stats(self, *args, **kwargs) -> dict:
		return {"stats": {}}

	def delete(self):
		raise NotImplementedError

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
		if self.yearly_fishing_permit or not all([self.year, self.member, self.organization]):
			# permit exists or required fields are missing
			return

		doctype = "Yearly Fishing Permit Type"
		if not self.type or not frappe.db.exists(doctype, self.type):
			default_type = "ALLG"
			if frappe.db.exists(doctype, default_type):
				self.type = default_type
			else:
				return

		create_yearly_fishing_permit(
			member=self.member,
			year=self.year,
			type=self.type,
			organization=self.organization,
		)

	def validate_existing_permit(self):
		if not self.yearly_fishing_permit:
			return

		existing_permit = frappe.get_doc("Yearly Fishing Permit", self.yearly_fishing_permit)
		remove_msg = _(
			"To create a new Yearly Fishing Permit, please remove the ID of the existing permit from the import."
		)
		if self.type != existing_permit.type:
			frappe.throw(
				_("You cannot change the type of a Yearly Fishing Permit through Member Data Import.")
				+ " "
				+ remove_msg
			)
		if self.year != existing_permit.year:
			frappe.throw(
				_("You cannot change the year of a Yearly Fishing Permit through Member Data Import.")
				+ " "
				+ remove_msg
			)
		if self.member != existing_permit.member:
			frappe.throw(
				_("You cannot change the member of a Yearly Fishing Permit through Member Data Import.")
				+ " "
				+ remove_msg
			)

	def update_doc(self, doc: Document, fields: "list[str]"):
		"""Update all `fields` of `doc` with the values from `self`."""
		has_changed = False
		for fieldname in fields:
			new_value = self.get(fieldname)
			if not new_value and not isinstance(new_value, int):  # int == 0 is allowed to disable checkbox
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
				new_value = (new_value or "").strip()

			if old_value != new_value:
				doc.set(fieldname, new_value)
				has_changed = True

		if has_changed:
			# Here we only update specific fields of an Address. This should be
			# possible, even if the user does not have the permissions to update
			# the Address record otherwise (e.g because it is linked to a Customer).
			ignore_permissions = doc.doctype == "Address"
			doc.save(ignore_permissions=ignore_permissions)


def create_member(organization: str, last_name: str) -> LANDAMember:
	"""Return a new LANDA Member."""
	member = frappe.new_doc("LANDA Member")
	member.organization = organization
	member.last_name = last_name

	return member.insert()


def create_address(address_line1: str, pincode: str, city: str, member: str, organization: str) -> None:
	"""Return a new Address linked to LANDA Member."""
	address = frappe.new_doc("Address")
	address.address_type = "Personal"
	address.address_line1 = address_line1
	address.pincode = pincode
	address.city = city
	address.country = "Germany"
	address.append("links", {"link_doctype": "LANDA Member", "link_name": member})
	address.organization = organization

	address.insert()


def create_yearly_fishing_permit(member: str, year: int, type: str, organization: str) -> None:
	data = {"member": member, "year": year, "type": type, "organization": organization}

	if frappe.db.exists("Yearly Fishing Permit", data):
		return

	yfp = frappe.new_doc("Yearly Fishing Permit")
	yfp.update(data)
	yfp.insert()


def parse_checkbox_value(value: str) -> int:
	scrubbed = value.strip().lower()

	return 1 if scrubbed in {"1", "ja", "j", "yes", "y"} else 0
