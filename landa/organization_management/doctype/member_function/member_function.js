// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member Function", {
	refresh: function (frm) {
		frm.trigger("set_member_function_category_query");
	},
	set_member_function_category_query: function (frm) {
		const query_args = {
			page_length: 50,
		};
		if (frappe.user.has_role("LANDA State Organization Employee")) {
			frm.set_query("member_function_category", () => {
				return query_args;
			});
		}

		if (frappe.user.has_role("LANDA Regional Organization Management")) {
			query_args.filters = {
				access_level: [
					"in",
					["Regional Organization", "Local Organization", "Local Group"],
				],
			};
		} else if (frappe.user.has_role("LANDA Local Organization Management")) {
			query_args.filters = {
				access_level: ["in", ["Local Organization", "Local Group"]],
			};
		} else if (frappe.user.has_role("LANDA Local Group Management")) {
			query_args.filters = {
				access_level: "Local Group",
			};
		}

		frm.set_query("member_function_category", () => {
			return query_args;
		});
	},
});
