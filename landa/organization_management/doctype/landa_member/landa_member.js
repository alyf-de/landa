// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("LANDA Member", {
	setup: function (frm) {
		// only the leaves of the organiztaion tree can have members
		frm.set_query("organization", function () {
			return {
				filters: {
					is_group: 0,
				},
			};
		});

		frm.make_methods = {
			User: () => {
				frappe.new_doc("User", {
					first_name: frm.doc.first_name,
					last_name: frm.doc.last_name,
					landa_member: frm.doc.name,
					organization: frm.doc.organization,
				});
			},
			"Work Assignment": () => {
				frappe.model.with_doctype("Work Assignment", () => {
					let new_doc = frappe.model.get_new_doc("Work Assignment");
					new_doc.organization = frm.doc.organization;

					let child = frappe.model.add_child(
						new_doc,
						"Work Assignment Member",
						"members",
					);
					child.member = frm.doc.name;

					frappe.set_route("Form", "Work Assignment", new_doc.name);
				});
			},
		};
	},
	refresh: function (frm) {
		// Automatically add the backlink to LANDA Member when a new Address or
		// Contact is added.
		frappe.dynamic_link = { doc: frm.doc, fieldname: "name", doctype: "LANDA Member" };

		// Display Address and Contact only after the LANDA Member has been created,
		// not on the initial form.
		frm.toggle_display(["section_address_and_contact"], !frm.doc.__islocal);

		if (frm.doc.__islocal) {
			frappe.contacts.clear_address_and_contact(frm);
		} else {
			frappe.contacts.render_address_and_contact(frm);
		}

		if (!frm.is_new()) {
			frappe.model.with_doctype("User", () => {
				// model needed for `frappe.perm.has_perm`
				if (!frappe.perm.has_perm("User", 0, "create")) {
					return;
				}

				frappe.db
					.get_value("User", { landa_member: frm.doc.name }, "name")
					.then((resp) => {
						if (resp.message.name) {
							return;
						}

						frm.add_custom_button(__("Create User"), function () {
							frm.make_methods["User"]();
						});
					});
			});

			frm.add_custom_button(
				__("Work Assignment"),
				function () {
					frm.make_methods["Work Assignment"]();
				},
				__("Create"),
			);
		}
	},
});
