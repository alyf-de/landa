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
			get_data: (txt) => {
				const fishing_areas = frappe.query_report.get_filter_value("fishing_area") || [];
				const filters = {};
				if (fishing_areas.length > 0) {
					filters.fishing_area = ["in", fishing_areas];
				}
				return frappe.db.get_link_options("Water Body", txt, filters);
			},
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
	];

	if (
		frappe.user.has_role([
			"Administrator",
			"System Manager",
			"LANDA State Organization Employee",
			"LANDA Regional Organization Management",
			"LANDA Regional Water Body Management",
		])
	) {
		extra_columns.push(
			{
				value: "share_of_avl",
				label: __("Share of AVL"),
				description: "",
			},
			{
				value: "share_of_avs",
				label: __("Share of AVS"),
				description: "",
			},
			{
				value: "share_of_ave",
				label: __("Share of AVE"),
				description: "",
			},
		);
	}

	return extra_columns.filter((d) => d.label.toLowerCase().includes(txt.toLowerCase()));
}
