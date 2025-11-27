// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Water Body Development"] = {
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
			get_data: (txt) =>
				frappe.db.get_link_options("Water Body", txt, {
					organization: frappe.boot.landa.regional_organization,
				}),
		},
		{
			fieldname: "fish_species",
			fieldtype: "MultiSelectList",
			label: __("Fish Species"),
			get_data: (txt) => frappe.db.get_link_options("Fish Species", txt),
		},
	],
};
