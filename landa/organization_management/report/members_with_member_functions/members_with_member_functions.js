// Copyright (c) 2016, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Members with Member Functions"] = {
	filters: [
		{
			fieldname: "member_function_category",
			fieldtype: "Link",
			options: "Member Function Category",
			label: __("Member Function Category"),
		},
		{
			fieldname: "organization",
			fieldtype: "Link",
			options: "Organization",
			label: __("Organization"),
			default: frappe.defaults.get_user_default("Organization"),
			get_query: function () {
				return {
					filters: {
						is_group: 0,
					},
				};
			},
		},
	],
};
