frappe.listview_settings["LANDA Member"] = {
	onload(list_view) {
		if (!frappe.user.has_role("System Manager")) {
			list_view.page.actions
				.find(`[data-label='${encodeURIComponent(__("Delete"))}']`)
				.closest("li")
				.addClass("hidden");
		}
	},
};
