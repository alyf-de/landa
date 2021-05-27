# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet
from frappe.desk.treeview import make_tree_args
from frappe.model.naming import make_autoname
from frappe.model.naming import revert_series_if_last
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.contacts.address_and_contact import delete_contact_and_address

class Organization(NestedSet):
	nsm_parent_field = 'parent_organization'

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
			self.name = make_autoname(self.parent_organization + '-.###', 'Organization')
		elif self.is_level(3):
			# Chapters
			self.name = make_autoname(self.parent_organization + '-.##', 'Organization')
		else:
			frappe.throw(_("Cannot set Parent Organization to a local group."))

	def after_insert(self):
		if self.is_level(1):
			# Regional Organizations
			self.create_company()
		elif self.is_level(2):
			# Local Organizations
			self.create_customer()

	def onload(self):
		load_address_and_contact(self)

	def on_update(self):
		super(Organization, self).on_update()

	def on_trash(self):
		delete_contact_and_address(self.doctype, self.name)
		self.revert_series()

		# NestedSet.on_trash should be the last command because it destroys the
		# funtionality of NestedSet. Some methods will not work properly afterwards.
		super(Organization, self).on_trash(allow_root_deletion=True)

	def revert_series(self):
		"""Decrease the naming counter when the newest organization gets deleted."""
		if self.is_level(0) or self.is_level(1):
			return

		# reconstruct the key used to generate the name
		number_part_len = len(self.name.split('-')[-1])
		key = self.name[:-number_part_len] + '.' + '#' * number_part_len

		revert_series_if_last(key, self.name)

	def is_level(self, n):
		"""Return True if the number of ancestors equals n"""
		if not self.parent_organization:
			return n == 0
		else:
			return frappe.get_doc(self.doctype, self.parent_organization).is_level(n - 1)

	def create_customer(self):
		"""Create a Customer corresponding to this organization."""
		customer = frappe.new_doc("Customer")
		# Name (ID) of Customer is determined by customer_name on insert ...
		customer.customer_name = self.name
		customer.insert()
		# ... so we can set the correct value only after insertion.
		customer.customer_name = self.organization_name
		customer.save()

		self.customer = customer.name
		self.save()

	def create_company(self):
		# erpnext.setup.setup_wizard.operations.install_fixtures + account_number
		def create_bank_account(args):
			if not args.bank_account:
				return

			company_name = args.company_name
			bank_account_group =  frappe.db.get_value("Account",
				{"account_type": "Bank", "is_group": 1, "root_type": "Asset",
					"company": company_name})
			if bank_account_group:
				bank_account = frappe.get_doc({
					"doctype": "Account",
					'account_name': args.bank_account,
					'account_number': args.account_number,
					'parent_account': bank_account_group,
					'is_group':0,
					'company': company_name,
					"account_type": "Bank",
				})
				try:
					doc = bank_account.insert()

					frappe.db.set_value("Company", args.company_name, "default_bank_account", bank_account.name, update_modified=False)

				except erpnext.accounts.doctype.account.account.RootNotEditable:
					frappe.throw(_("Bank account cannot be named as {0}").format(args.bank_account))
				except frappe.DuplicateEntryError:
					# bank account same as a CoA entry
					pass

		if frappe.db.exists('Company', self.organization_name):
			return

		company = frappe.new_doc('Company')
		company.company_name = self.organization_name
		company.abbr = self.name
		company.default_currency = 'EUR'
		company.country = 'Germany'
		company.create_chart_of_accounts_based_on = 'Standard Template'
		company.chart_of_accounts = 'Standard with Numbers'
		company.save()

		create_bank_account(frappe._dict(
			{
				'bank_account': 'Default Bank Account',
				'account_number': '1201',
				'company_name': self.organization_name
			}
		))

@frappe.whitelist()
def get_children(doctype, parent=None, organization=None, is_root=False):
	if parent == None or parent == "All Organizations":
		parent = ""

	return frappe.db.get_all(doctype, fields=[
			'name as value',
			'organization_name as title',
			'is_group as expandable'
		],
		filters={
			'parent_organization': parent
		}
	)


@frappe.whitelist()
def add_node():
	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_organization == 'All Organizations':
		args.parent_organization = None

	frappe.get_doc(args).insert()
