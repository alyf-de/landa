// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stocking of Supported Water Bodies"] = {
	filters: [
		{
			fieldname: "year",
			fieldtype: "Select",
			label: __("Year"),
			options: "\n2021\n2022\n2023\n2024\n2025\n2026\n2027\n2028\n2029",
			mandatory: 0,
			wildcard_filter: 0,
			default: moment().year() - 1,
		},
		{
			fieldname: "water_body",
			fieldtype: "Link",
			options: "Water Body",
			label: __("Water Body"),
			mandatory: 0,
			wildcard_filter: 0,
		},
		{
			fieldname: "fish_species",
			fieldtype: "Link",
			label: __("Fish Species"),
			options: "Fish Species",
			mandatory: 0,
			wildcard_filter: 0,
		},
		{
			fieldname: "fish_type_for_stocking",
			fieldtype: "Link",
			label: __("Fish Type For Stocking"),
			options: "Fish Type For Stocking",
			mandatory: 0,
			wildcard_filter: 0,
		},
	],
};
