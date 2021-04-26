# Copyright (c) 2013, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

class LandaCustomerLedger(object):

	def __init__(self, filters):
		if 'organization' in filters:
			filters['customer'] = frappe.db.get_value('Organization', filters.get('organization'), 'customer')

		self.filters = filters

	def run(self):
		if not ('company' in self.filters and 'customer' in self.filters):
			return [], []

		return self.get_columns(), self.get_data()

	def get_data(self):
		query = """
			SELECT
				posting_date,
				voucher_type,
				voucher_no,
				case debit when 0 then -1 * credit else debit end as outstanding_amount
			FROM `tabGL Entry`
			WHERE party_type = 'Customer'
			AND company = %(company)s
			AND party = %(customer)s
		"""

		if self.filters.get('fiscal_year'):
			query += " AND fiscal_year = %(fiscal_year)s"

		query += " ORDER BY posting_date, creation ASC"

		return frappe.db.sql(query, self.filters)

	def get_columns(self):
		return [
			{
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"label": "Posting Date",
				"width": 200
			},
			{
				"fieldname": "voucher_type",
				"fieldtype": "Link",
				"label": "Voucher Type",
				"options": "DocType",
				"width": 200
			},
			{
				"fieldname": "voucher_no",
				"fieldtype": "Dynamic Link",
				"label": "Voucher No",
				"options": "voucher_type",
				"width": 200
			},
			{
				"fieldname": "outstanding_amount",
				"fieldtype": "Currency",
				"label": "Outstanding Amount",
				"width": 200
			}
		]


def execute(filters=None):
	return LandaCustomerLedger(filters).run()
