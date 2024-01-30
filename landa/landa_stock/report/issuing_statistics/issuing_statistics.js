// Copyright (c) 2024, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Issuing statistics"] = {
	filters: [
		{
			fieldname: "year_of_settlement",
			label: __("Year of Settlement"),
			fieldtype: "Int",
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		}
	],
};
