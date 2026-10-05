// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.query_reports["Work Ledger Balance"] = {
	filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			options: get_year_options(),
			default: new Date().getFullYear().toString(),
		},
		{
			fieldname: "organization",
			label: __("Organization"),
			fieldtype: "Link",
			options: "Organization",
			get_query: function () {
				return { filters: { is_group: 0 } };
			},
		},
		{
			fieldname: "member",
			label: __("Member"),
			fieldtype: "Link",
			options: "LANDA Member",
		},
	],
};

function get_year_options() {
	const current_year = new Date().getFullYear();
	const years = [];
	for (let i = current_year; i >= current_year - 10; i--) {
		years.push(i.toString());
	}
	return years.join("\n");
}
