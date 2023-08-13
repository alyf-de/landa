// Copyright (c) 2023, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LANDA Deliveries and Payments Summaries"] = {
	"filters": [
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"label": "Organization",
			"mandatory": 0,
			"options": "Organization",
			"wildcard_filter": 0,
			"default": frappe.defaults.get_user_default("Organization"),
			"get_query": function() {
				return {
					filters: [
						["parent_organization", "in", ["AVS", "AVL", "AVE"]]
					]
				}
			}
		},
		{
			"fieldname": "year_of_settlement",
			"fieldtype": "Data",
			"label": "Year of Settlement",
			"mandatory": 0,
			"wildcard_filter": 0,
			"default": new Date().getFullYear()
		}
	]
};
