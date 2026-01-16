frappe.listview_settings["LANDA Member"] = {
	onload(list_view) {
		if (!frappe.user.has_role("System Manager")) {
			// remove the default delete button
			list_view.page.actions
				.find(`[data-label='${encodeURIComponent(__("Delete"))}']`)
				.closest("li")
				.remove();

			if (frappe.model.can_delete(doctype) && !frappe.model.has_workflow(doctype)) {
				// add our own delete button with password prompt
				list_view.page.add_actions_menu_item(
					__("Delete", null, "Button in list view actions menu"),
					() => {
						const docnames = list_view
							.get_checked_items(true)
							.map((docname) => docname.toString());
						if (docnames.length === 1) {
							run_bulk_delete(list_view, docnames);
							return;
						}

						frappe.prompt(
							[
								{
									fieldname: "password",
									fieldtype: "Password",
									label: __("Password"),
									reqd: 1,
								},
							],
							(values) => {
								frappe
									.xcall("landa.auth.check_password", {
										password: values.password,
									})
									.then((result) => {
										if (!result) {
											frappe.msgprint(__("Incorrect password"));
											return;
										}

										run_bulk_delete(list_view, docnames);
									});
							},
							__("Delete {0} items permanently?", [docnames.length]),
							__("Delete")
						);
					},
					true
				);
			}
		}

		if (frappe.model.can_write("LANDA Member")) {
			list_view.page.add_action_item(__("Clear Special Fishing Permits"), () => {
				const members = list_view.get_checked_items(true);
				frappe.confirm(
					__(
						"Are you sure you want to clear all Special Yearly Fishing Permits for the {0} selected members?",
						[members.length],
					),
					() => {
						frappe
							.xcall(
								"landa.organization_management.doctype.landa_member.landa_member.clear_special_yearly_fishing_permits",
								{ members: members },
							)
							.then(() => {
								frappe.show_alert({
									message: __("Special Yearly Fishing Permits cleared."),
									indicator: "green",
								});
								list_view.refresh();
							});
					},
				);
			});
		}

		if (frappe.model.can_create("Yearly Fishing Permit")) {
			list_view.page.add_action_item(__("Create Yearly Fishing Permit"), () => {
				frappe.prompt(
					[
						{
							fieldname: "permit_type",
							fieldtype: "Link",
							label: __("Type"),
							options: "Yearly Fishing Permit Type",
							default: "ALLG",
							reqd: 1,
						},
						{
							fieldname: "year",
							fieldtype: "Int",
							label: __("Year"),
							default: landa.utils.get_default_year(),
							reqd: 1,
						},
					],
					(values) => {
						frappe
							.xcall(
								"landa.organization_management.doctype.yearly_fishing_permit.yearly_fishing_permit.bulk_create",
								{
									permit_type: values.permit_type,
									year: values.year,
									members: list_view.get_checked_items(true),
								}
							)
							.then((total_created) => {
								frappe.show_alert({
									message: __(
										"Yearly Fishing Permits have been created for {0} members.",
										[total_created]
									),
									indicator: "green",
								});
								list_view.refresh();
							});
					}
				);
			});
		}
	},
};

function run_bulk_delete(list_view, docnames) {
	list_view.disable_list_update = true;
	bulk_delete(list_view.doctype, docnames, () => {
		list_view.disable_list_update = false;
		list_view.clear_checked_items();
		list_view.refresh();
	});
}

// copied from frappe/public/js/frappe/list/bulk_operations.js
function bulk_delete(doctype, docnames, done) {
	frappe
		.call({
			method: "frappe.desk.reportview.delete_items",
			freeze: true,
			freeze_message:
				docnames.length <= 10 ? __("Deleting {0} records...", [docnames.length]) : null,
			args: {
				items: docnames,
				doctype: doctype,
			},
		})
		.then((r) => {
			let failed = r.message;
			if (!failed) {
				failed = [];
			}

			if (failed.length && !r._server_messages) {
				frappe.throw(__("Cannot delete {0}", [failed.map((f) => f.bold()).join(", ")]));
			}
			if (failed.length < docnames.length) {
				frappe.utils.play_sound("delete");
				if (done) {
					done();
				}
			}
		});
}
