# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe


class LANDAMemberCount:
	def __init__(self, filters):
		if "organization" in filters and filters["organization"] in ["AVL", "AVS", "AVE"]:
			filters["company"] = frappe.get_value(
				"Organization", filters.get("organization"), "organization_name"
			)
			filters["company_abbr"] = filters.pop("organization")
		else:
			filters["total"] = 0

		self.filters = filters

	def run(self):
		if "company" in self.filters or "organization" in self.filters:
			return self.get_columns(), self.get_data()
		else:
			return [], []

	def get_data(self):
		sql_query = """
			SELECT CASE WHEN %s = 0 THEN dn.customer ELSE %s END,
				CASE WHEN %s = 0 THEN dn.customer_name ELSE dn.company END,
				-- cast to make it usable on x-axis in a chart
				CAST(dn.year_of_settlement AS CHAR(4)),
				SUM(CASE WHEN iva.attribute_value = 'Vollzahler' THEN dni.qty ELSE 0 END),
				SUM(CASE WHEN iva.attribute_value = 'Jugend' THEN dni.qty ELSE 0 END),
				SUM(CASE WHEN iva.attribute_value = 'Fördermitglied' THEN dni.qty ELSE 0 END),
				SUM(CASE WHEN iva.attribute_value = 'Austauschmarke' THEN dni.qty ELSE 0 END)
			FROM `tabDelivery Note Item` dni
			JOIN `tabItem` i ON dni.item_code = i.item_code
			JOIN `tabItem Variant Attribute` iva ON dni.item_code = iva.parent
			JOIN `tabDelivery Note` dn ON dni.parent = dn.name
			WHERE iva.attribute = "Beitragsart"
				AND dn.docstatus = 1
				AND dn.year_of_settlement LIKE %s
				AND dn.organization LIKE %s
				AND dn.company LIKE %s
			GROUP BY dn.year_of_settlement, CASE WHEN %s = 0 THEN dn.customer ELSE dn.company END
			ORDER BY dn.customer, dn.year_of_settlement
			"""

		return frappe.db.sql(
			sql_query,
			(
				self.filters.get("total", 0),
				self.filters.get("company_abbr", ""),
				self.filters.get("total", 0),
				self.filters.get("year", "%"),
				self.filters.get("organization", "%"),
				self.filters.get("company", "%"),
				self.filters.get("total", 0),
			),
		)

	def get_columns(self):
		return [
			{
				"fieldname": "organization",
				"fieldtype": "Link",
				"label": "Organization",
				"options": "Organization",
				"width": 150,
			},
			{
				"fieldname": "customer_name",
				"fieldtype": "Data",
				"label": "Organization Name",
				"width": 250,
			},
			{"fieldname": "year", "fieldtype": "Data", "label": "Year", "width": 150},
			{
				"fieldname": "vollzahler",
				"fieldtype": "Data",
				"label": "Vollzahler",
				"width": 150,
			},
			{"fieldname": "jugend", "fieldtype": "Data", "label": "Jugend", "width": 150},
			{
				"fieldname": "foerdermitglied",
				"fieldtype": "Data",
				"label": "Fördermitglied",
				"width": 150,
			},
			{
				"fieldname": "austauschmarke",
				"fieldtype": "Data",
				"label": "Austauschmarke",
				"width": 150,
			},
		]


def execute(filters=None):
	return LANDAMemberCount(filters).run()
