// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LANDA Member Count"] = {
	"filters": [
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"label": __("Organization"),
			"mandatory": 1,
			"options": "Organization",
			"wildcard_filter": 0,
			"default": frappe.defaults.get_user_default("Organization"),
			"get_query": function() {
				return {
					filters: [
						["Organization", "parent_organization", "in", ["LV", "AVL", "AVS", "AVE"]]
					]
				}
			}
		},
		{
			"fieldname": "year",
			"fieldtype": "Data",
			"label": __("Year"),
			"mandatory": 0,
			"wildcard_filter": 0,
		},
		{
			"fieldname": "total",
			"fieldtype": "Check",
			"label": __("Total (only for regional org.)"),
			"mandatory": 0,
			"wildcard_filter": 0,
		}
	]
};