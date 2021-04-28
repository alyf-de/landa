// Copyright (c) 2016, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LANDA Customer Ledger"] = {
	"filters": [
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": "Company",
			"mandatory": 1,
			"options": "Company",
			"wildcard_filter": 0,
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"label": "Organization",
			"mandatory": 1,
			"options": "Organization",
			"wildcard_filter": 0
		},
		{
			"fieldname": "fiscal_year",
			"fieldtype": "Link",
			"label": "Fiscal Year",
			"mandatory": 0,
			"options": "Fiscal Year",
			"wildcard_filter": 0
		}
	]
};
