// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member Function", {
	refresh: function (frm) {
		frm.trigger("set_member_function_category_query");
	},
	set_member_function_category_query: function (frm) {
		if (frappe.user.has_role("LANDA State Organization Employee")) return;

		if (frappe.user.has_role("LANDA Regional Organization Management")) {
			frm.set_query("member_function_category", () => {
				return {
					filters: {
						access_level: ["in", ["Regional Organization", "Local Organization"]],
					},
				};
			});
		} else if (frappe.user.has_role("LANDA Local Organization Management")) {
			frm.set_query("member_function_category", () => {
				return {
					filters: {
						access_level: "Local Organization",
					},
				};
			});
		} else if (frappe.user.has_role("LANDA Local Group Management")) {
			frm.set_query("member_function_category", () => {
				return {
					filters: {
						access_level: "Local Group",
					},
				};
			});
		}
	},
});
