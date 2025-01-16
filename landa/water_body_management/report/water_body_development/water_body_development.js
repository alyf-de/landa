// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

const year_range = (past_years, future_years) => {
	const current_year = new Date().getFullYear();
	const start_year = current_year - past_years;
	const end_year = current_year + future_years;
	return Array.from({ length: end_year - start_year + 1 }, (_, i) => start_year + i);
}

const five_years = year_range(5, 0);
const default_year = new Date().getFullYear();

frappe.query_reports["Water Body Development"] = {
	filters: [
		{
			fieldname: "from_year",
			label: __("From Year"),
			fieldtype: "Select",
			options: five_years,
			default: default_year,
		},
		{
			fieldname: "to_year",
			label: __("To Year"),
			fieldtype: "Select",
			options: five_years,
			default: default_year,
		},
	],
};

