// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Catch Log Statistics"] = {
	filters: [
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
		{
			fieldname: "water_body",
			fieldtype: "MultiSelectList",
			label: __("Water Body"),
			get_data: (txt) => frappe.db.get_link_options("Water Body", txt),
		},
		{
			fieldname: "fish_species",
			fieldtype: "MultiSelectList",
			label: __("Fish Species"),
			get_data: (txt) => frappe.db.get_link_options("Fish Species", txt),
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
			fieldname: "show_by_foreign_regional_org",
			fieldtype: "Check",
			label: "Show Share of other Regional Organizations",
			hidden: !frappe.user.has_role(
				[
					"Administrator",
					"System Manager",
					"LANDA State Organization Employee",
					"LANDA Regional Organization Management",
					"LANDA Regional Water Body Management",
				]
			),
		},
		{
			fieldname: "show_area_name",
			fieldtype: "Check",
			label: "Show Area Name",
		},
	],
};
