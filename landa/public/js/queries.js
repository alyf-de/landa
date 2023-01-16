frappe.provide("landa");

landa.queries = {
	regional_organization_query: function (doc) {
		return {
			filters: {
				parent_organization: frappe.boot.landa.state_organization ?? "LV",
			},
		};
	},
};
