// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Fishing Days by Organization"] = {
	filters: [
		{
			fieldname: "organization",
			fieldtype: "Link",
			label: __("Organization"),
			options: "Organization",
			get_query: () => ({ filters: { is_group: 0 } }),
		},
		{
			fieldname: "water_body",
			fieldtype: "Link",
			label: __("Water Body"),
			options: "Water Body",
			reqd: 1,
		},
		{
			fieldname: "from_year",
			fieldtype: "Int",
			label: __("From Year"),
			default: moment().year() - 1,
		},
		{
			fieldname: "to_year",
			fieldtype: "Int",
			label: __("To Year"),
			default: moment().year(),
		},
	],
};
