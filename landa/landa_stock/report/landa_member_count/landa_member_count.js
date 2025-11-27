// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LANDA Member Count"] = {
	filters: [
		{
			fieldname: "organization",
			fieldtype: "Link",
			label: __("Organization"),
			mandatory: 1,
			options: "Organization",
			wildcard_filter: 0,
			default: frappe.defaults.get_user_default("Organization"),
			get_query: function () {
				return {
					filters: [
						["Organization", "parent_organization", "in", ["LV", "AVL", "AVS", "AVE"]],
					],
				};
			},
		},
		{
			fieldname: "year",
			fieldtype: "Data",
			label: __("Year"),
			wildcard_filter: 0,
		},
		{
			fieldname: "fishing_area",
			fieldtype: "Link",
			label: __("Fishing Area"),
			options: "Fishing Area",
			depends_on:
				'eval: (frappe.query_report.get_filter_value("organization") || "").length === 3', // show ony if regional org is selected
			get_query: function () {
				const selected_org = frappe.query_report.get_filter_value("organization");
				if (!selected_org) {
					return {};
				}

				return {
					filters: {
						organization: selected_org.substring(0, 3),
					},
				};
			},
		},
		{
			fieldname: "total",
			fieldtype: "Check",
			label: __("Total (only for regional org.)"),
			wildcard_filter: 0,
		},
	],
};
