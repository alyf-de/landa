# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import List

import frappe
from frappe import _
from frappe.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)
from frappe.desk.treeview import make_tree_args
from frappe.model.naming import make_autoname, revert_series_if_last
from frappe.permissions import has_permission
from frappe.utils.data import cint, get_link_to_form
from frappe.utils.nestedset import NestedSet

from landa.organization_management.doctype.landa_member.landa_member import get_address_or_contact


class Organization(NestedSet):
	nsm_parent_field = "parent_organization"

	def autoname(self):
		"""Generate the unique organization number (name field)

		Top-Level-Organization:		according to short code (LVSA, AVL, AVE, ...)
		Organization:				AVL-001, AVE-001, ...
		Local group:				AVL-001-01, AVL-001-02, ...
		"""
		if self.name:
			return

		if self.is_level(0) or self.is_level(1):
			# State and Regional Organizations
			self.name = self.short_code
		elif not self.parent_organization:
			frappe.throw(_("Please set a Parent Organization."))
		elif self.is_level(2):
			# Local Organizations
			self.name = make_autoname(self.parent_organization + "-.###", "Organization")
		elif self.is_level(3):
			# Chapters
			self.name = make_autoname(self.parent_organization + "-.##", "Organization")
		else:
			frappe.throw(_("Cannot set Parent Organization to a local group."))

	def after_insert(self):
		if self.is_level(1):
			# Regional Organizations
			self.create_company()
		elif self.is_level(2):
			# Local Organizations
			self.create_customer()

		# Clear user permissions cache, so users can work with the new
		# Organization right away. If we don't do this, users will get a
		# permission error when trying to read the Organization. This is because
		# all the permitted Organizations get cached and the new one is not part
		# of it yet.
		frappe.cache().delete_key("user_permissions")

	def onload(self):
		load_address_and_contact(self)

	def on_update(self):
		super().on_update()

	def on_trash(self):
		delete_contact_and_address(self.doctype, self.name)
		self.revert_series()

		# NestedSet.on_trash should be the last command because it destroys the
		# funtionality of NestedSet. Some methods will not work properly afterwards.
		super().on_trash(allow_root_deletion=True)

	@frappe.whitelist()
	def get_series_current(self):
		frappe.only_for("System Manager")
		return frappe.db.get_value("Series", self.name + "-", "current", order_by="name") or 0

	@frappe.whitelist()
	def set_series_current(self, current):
		frappe.only_for("System Manager")
		series = self.name + "-"

		# insert series if missing
		if frappe.db.get_value("Series", series, "name", order_by="name") is None:
			frappe.db.sql("insert into tabSeries (name, current) values (%s, 0)", (series))

		frappe.db.sql("UPDATE `tabSeries` SET current = %s WHERE name = %s", (cint(current), series))

	def revert_series(self):
		"""Decrease the naming counter when the newest organization gets deleted."""
		if self.is_level(0) or self.is_level(1):
			return

		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split("-")[-1])
		key = self.name[:-number_part_len] + "." + "#" * number_part_len

		revert_series_if_last(key, self.name)

	def is_level(self, n):
		"""Return True if the number of ancestors equals n"""
		if not self.parent_organization:
			return n == 0
		else:
			return frappe.get_doc(self.doctype, self.parent_organization).is_level(n - 1)

	def create_customer(self):
		"""Create a Customer corresponding to this organization."""
		# check permission here so we can ignore it later
		self.check_permission_on_parent("create")

		customer = frappe.new_doc("Customer")
		# Name (ID) of Customer is determined by customer_name on insert ...
		customer.customer_name = self.name
		customer.organization = self.name
		customer.insert(ignore_permissions=True)
		# ... so we can set the correct value only after insertion.
		customer.customer_name = self.organization_name
		customer.save(ignore_permissions=True)

	def create_company(self):
		def create_bank_account(bank_account, account_number, company_name):
			bank_account_group = frappe.db.get_value(
				"Account",
				{
					"account_type": "Bank",
					"is_group": 1,
					"root_type": "Asset",
					"company": company_name,
				},
			)
			if bank_account_group:
				bank_account = frappe.get_doc(
					{
						"doctype": "Account",
						"account_name": bank_account,
						"account_number": account_number,
						"parent_account": bank_account_group,
						"is_group": 0,
						"company": company_name,
						"account_type": "Bank",
					}
				)

				bank_account.insert()
				frappe.db.set_value(
					"Company",
					company_name,
					"default_bank_account",
					bank_account.name,
					update_modified=False,
				)

		def set_mode_of_payment_account(docname, company, default_account):
			frappe.get_doc("Mode of Payment", docname).append(
				"accounts", {"company": company, "default_account": default_account}
			).save()

		if frappe.db.exists("Company", self.organization_name):
			return

		company = frappe.new_doc("Company")
		company.company_name = self.organization_name
		company.abbr = self.name
		company.default_currency = "EUR"
		company.country = "Germany"
		company.create_chart_of_accounts_based_on = "Standard Template"
		company.chart_of_accounts = "Standard with Numbers"
		company.save()

		create_bank_account("Default Bank Account", "1201", company.name)

		set_mode_of_payment_account(
			"Banküberweisung",
			company.name,
			frappe.get_value("Company", company.name, "default_bank_account"),
		)

		set_mode_of_payment_account(
			"Bar",
			company.name,
			frappe.get_value("Company", company.name, "default_cash_account"),
		)

	def check_permission_on_parent(self, ptype):
		"""Check if current user has `ptype` permission on parent Organization.

		User Permission check against this DocType will fail during initial creation.
		Therefore we check if we have permission on the parent doctype and can safely
		ignore permissions afterwards.
		"""
		parent_organization = frappe.get_doc("Organization", self.parent_organization)
		if not has_permission("Organization", ptype=ptype, doc=parent_organization):
			frappe.throw(_("Not permitted"), frappe.PermissionError)

	@frappe.whitelist()
	def link_contact(
		self, landa_member: str, is_default_billing: int = 0, is_default_shipping: int = 0
	):
		self.has_permission("write")

		contact = get_address_or_contact("Contact", landa_member)
		if not contact:
			frappe.throw(
				_("There is no single contact linked to {0}.").format(
					get_link_to_form("LANDA Member", landa_member)
				)
			)

		address = get_address_or_contact("Address", landa_member)
		if not address:
			frappe.throw(
				_("There is no single address linked to {0}.").format(
					get_link_to_form("LANDA Member", landa_member)
				)
			)

		add_links(contact, self.name)
		add_links(address, self.name)

		customer = frappe.get_doc("Customer", self.name)
		if is_default_billing:
			customer.default_billing_contact = contact.name
			customer.default_billing_address = address.name
		if is_default_shipping:
			customer.default_shipping_contact = contact.name
			customer.default_shipping_address = address.name

		customer.save()


def add_links(address_or_contact, organization: str):
	existing_links = {(link.link_doctype, link.link_name) for link in address_or_contact.links}
	for doctype in ("Organization", "Customer"):
		if (doctype, organization) not in existing_links:
			address_or_contact.append(
				"links",
				{
					"link_doctype": doctype,
					"link_name": organization,
				},
			)

	address_or_contact.save()


@frappe.whitelist()
def get_children(doctype, parent=None, organization=None, is_root=False):
	if parent is None or parent == "All Organizations":
		parent = ""

	return frappe.get_list(
		doctype,
		fields=[
			"name as value",
			"organization_name as title",
			"is_group as expandable",
		],
		filters={"parent_organization": parent},
		ignore_permissions=parent in ("LV", ""),
	)


@frappe.whitelist()
def add_node():
	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_organization == "All Organizations":
		args.parent_organization = None

	doc = frappe.get_doc(args)
	doc.check_permission_on_parent("create")
	doc.insert(ignore_permissions=True)


def get_supported_water_bodies(organization: str) -> List[str]:
	"""Return a list of water bodies that are supported by the organization."""
	return frappe.get_all(
		"Water Body Management Local Organization",
		filters={"organization": organization, "disabled": 0},
		pluck="water_body",
	)
