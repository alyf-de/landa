// Copyright (c) 2016, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LANDA Deliveries and Payments"] = {
	"filters": [
		{
			"fieldname": "parent_organization",
			"fieldtype": "Link",
			"label": "Parent Organization",
			"mandatory": 1,
			"options": "Organization",
			"wildcard_filter": 0,
			"get_query": function() {
				return {
					filters: {
						parent_organization: 'LV'
					}
				}
			}
		},
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"label": "Organization",
			"mandatory": 1,
			"options": "Organization",
			"wildcard_filter": 0,
			"get_query": function() {
				return {
					filters: [
						["Organization", "parent_organization", "=", frappe.query_report.get_filter_value('parent_organization')],
						["Organization", "customer", "is", "set"],
					]
				}
			}
		},
		{
			"fieldname": "year_of_settlement",
			"fieldtype": "Data",
			"label": "Year of Settlement",
			"mandatory": 0,
			"wildcard_filter": 0
		}
	]
};
