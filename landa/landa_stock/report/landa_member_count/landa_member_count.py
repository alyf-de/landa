# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

class LANDAMemberCount(object):

	def __init__(self, filters):
		if 'organization' in filters:
			company, customer = frappe.get_value(
				'Organization',
				filters.pop('organization'),
				['organization_name', 'customer']
			)

			if customer:
				filters['customer'] = customer
			elif company:
				filters['company'] = company

		self.filters = filters

	def run(self):
		if 'company' in self.filters or 'customer' in self.filters:
			return self.get_columns(), self.get_data()
		else:
			return [], []


	def get_data(self):
		sql_query = """
			SELECT dn.customer,
				dn.customer_name,
				iva.attribute_value,
				dn.year_of_settlement,
				SUM(dni.qty)
			FROM `tabDelivery Note Item` dni
			JOIN `tabItem` i ON dni.item_code = i.item_code
			JOIN `tabItem Variant Attribute` iva ON dni.item_code = iva.parent
			JOIN `tabDelivery Note` dn ON dni.parent = dn.name
			WHERE iva.attribute = "Beitragsart"
				AND dn.docstatus = 1
				AND dn.year_of_settlement LIKE %s
				AND iva.attribute_value LIKE %s
				AND dn.customer LIKE %s
				AND dn.company LIKE %s
			GROUP BY dni.item_code, dn.year_of_settlement, dn.customer
			ORDER BY dn.customer, iva.attribute_value, dn.year_of_settlement
			"""
		
		return frappe.db.sql(sql_query, (
			self.filters.get('year_of_settlement', '%'),
			self.filters.get('beitragsart', '%'),
			self.filters.get('customer', '%'),
			self.filters.get('company', '%')
		))


	def get_columns(self):
		return [
			{
				"fieldname": "organization",
				"fieldtype": "Link",
				"label": "Organization",
				"options": "Organization",
				"width": 150
			},
			{
				"fieldname": "customer_name",
				"fieldtype": "Data",
				"label": "Organization Name",
				"width": 250
			},
			{
				"fieldname": "beitragsart",
				"fieldtype": "Data",
				"label": "Beitragsart",
				"width": 200
			},
			{
				"fieldname": "year_of_settlement",
				"fieldtype": "Data",
				"label": "Year Of Settlement",
				"width": 150
			},
			{
				"fieldname": "count",
				"fieldtype": "Data",
				"label": "Count",
				"width": 100
			}
		]

def execute(filters=None):
	return LANDAMemberCount(filters).run()
