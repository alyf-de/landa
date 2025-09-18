// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lease Contract Payments"] = {
	filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Int",
			reqd: 1,
			default: new Date().getFullYear(),
		},
		{
			fieldname: "water_body",
			label: __("Water Body"),
			fieldtype: "Link",
			options: "Water Body",
			get_query: () => {
				if (!frappe.boot.landa.regional_organization) {
					return {};
				}

				return {
					filters: {
						organization: frappe.boot.landa.regional_organization,
					},
				};
			},
		},
		{
			fieldname: "fishing_area",
			label: __("Fishing Area"),
			fieldtype: "Link",
			options: "Fishing Area",
			get_query: () => {
				if (!frappe.boot.landa.regional_organization) {
					return {};
				}

				return {
					filters: {
						organization: frappe.boot.landa.regional_organization,
					},
				};
			},
		},
		{
			fieldname: "lease_object",
			label: __("Lease Object"),
			fieldtype: "Link",
			options: "Lease Object",
		},
		{
			fieldname: "landlord",
			label: __("Landlord"),
			fieldtype: "Link",
			options: "Landlord",
		},
	],
};
