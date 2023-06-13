// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Catch Log Days and Counts"] = {
	filters: [
		{
			fieldname: "from_year",
			fieldtype: "Int",
			label: __("From Year"),
			mandatory: 0,
			wildcard_filter: 0,
			default: moment().year() - 1,
		},
		{
			fieldname: "to_year",
			fieldtype: "Int",
			label: __("To Year"),
			mandatory: 0,
			wildcard_filter: 0,
			default: moment().year(),
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
			fieldname: "organization",
			fieldtype: "Link",
			options: "Organization",
			label: __("Organization"),
			mandatory: 0,
			wildcard_filter: 0,
			default: frappe.defaults.get_user_default("Organization"),
		},
		{
			fieldname: "fishing_area",
			fieldtype: "Link",
			options: "Fishing Area",
			label: __("Fishing Area"),
			mandatory: 0,
			wildcard_filter: 0,
		},
		{
			fieldname: "origin_of_catch_log_entry",
			fieldtype: "Select",
			label: __("Origin of Catch Log Entry"),
			options: "\nVerein\nRegionalverband",
		},
	],
};
