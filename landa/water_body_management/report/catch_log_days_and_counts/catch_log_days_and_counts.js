// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Catch Log Days and Counts"] = {
	filters: [
		{
			fieldname: "year",
			fieldtype: "Int",
			label: __("Year"),
			default: moment().year() - 1,
		},
		{
			fieldname: "water_body",
			fieldtype: "MultiSelectList",
			label: __("Water Body"),
			get_data: (txt) => frappe.db.get_link_options("Water Body", txt),
		},
		{
			fieldname: "organization",
			fieldtype: "Link",
			options: "Organization",
			label: __("Organization"),
			default: frappe.defaults.get_user_default("Organization"),
		},
		{
			fieldname: "fishing_area",
			fieldtype: "MultiSelectList",
			label: __("Fishing Area"),
			get_data: (txt) => frappe.db.get_link_options("Fishing Area", txt),
		},
		{
			fieldname: "origin_of_catch_log_entry",
			fieldtype: "Select",
			label: __("Origin of Catch Log Entry"),
			options: "\nVerein\nRegionalverband",
		},
		{
			fieldname: "extra_columns",
			fieldtype: "MultiSelectList",
			label: __("Extra Columns"),
			get_data: get_extra_columns,
		},
	],
};


function get_extra_columns(txt) {
	const extra_columns = [
		{
			value: "area_name",
			label: __("Area Name"),
			description: "",
		},
		{
			value: "water_body_size",
			label: __("Water Body Size"),
			description: "",
		},
		{
			value: "water_body_status",
			label: __("Water Body Status"),
			description: "",
		},
	]

	return extra_columns.filter((d) => d.label.toLowerCase().includes(txt.toLowerCase()));
}
