// Copyright (c) 2024, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Billing History"] = {
	filters: [
		{
			fieldname: "organization",
			fieldtype: "Link",
			label: "Organization",
			options: "Organization",
			reqd: 1,
			default: frappe.boot.landa.organization,
			get_query: function () {
				return {
					filters: {
						parent_organization: frappe.boot.landa.regional_organization,
					},
				};
			},
		},
		{
			fieldname: "year_of_settlement",
			fieldtype: "Int",
			label: "Year of Settlement",
			default: new Date().getFullYear(),
		},
	],
};
