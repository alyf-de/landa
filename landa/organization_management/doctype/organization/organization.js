// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Organization", {
	setup: function (frm) {
		disable_map_controls(frm.fields_dict["location"]);
	},
	onload: function (frm) {
		frm.trigger("set_fishing_area_query");
	},
	set_fishing_area_query: function (frm) {
		if (!frm.doc.parent_organization || frm.doc.parent_organization === "LV") {
			// If we're in a state or regional Organization, this doesn't make
			// sense because Fishing Area depends on regional Organization.
			return;
		}

		// allow only fishing areas within the own regional organization
		frm.set_query("fishing_area", function (doc) {
			return {
				filters: {
					// own regional organization is determined by the first
					// three letters of the parent organization
					organization: doc.parent_organization.substring(0, 3),
				},
			};
		});
	},
	refresh: function (frm) {
		// Automatically add the backlink to Organization when a new Address or
		// Contact is added.
		frappe.dynamic_link = { doc: frm.doc, fieldname: "name", doctype: "Organization" };

		// Display Address and Contact only after the Member has been created,
		// not on the initial form.
		frm.toggle_display(["section_address_and_contact"], !frm.doc.__islocal);

		if (frm.doc.__islocal) {
			frappe.contacts.clear_address_and_contact(frm);
		} else {
			frappe.contacts.render_address_and_contact(frm);
		}

		if (frappe.user.has_role("System Manager") && !frm.is_dirty()) {
			frm.page.add_menu_item(__("Update Naming Series"), () =>
				frm.trigger("update_naming_series")
			);
		}

		if (!frm.is_dirty() && frm.has_perm("write")) {
			frm.page.add_menu_item(__("Link Member as Contact"), () => {
				frappe.prompt(
					[
						{
							fieldname: "landa_member",
							label: __("LANDA Member"),
							fieldtype: "Link",
							options: "LANDA Member",
							reqd: 1,
							get_query: function () {
								return {
									filters: {
										organization: frm.doc.name,
									},
								};
							},
						},
						{
							fieldname: "is_default_billing",
							label: __("Is Default Billing Contact"),
							fieldtype: "Check",
							reqd: 1,
						},
						{
							fieldname: "is_default_shipping",
							label: __("Is Default Shipping Contact"),
							fieldtype: "Check",
							reqd: 1,
						},
					],
					(values) => {
						frm.call({
							method: "link_contact",
							doc: frm.doc,
							freeze: true,
							freeze_message: __("Linking Contact ..."),
							args: {
								landa_member: values.landa_member,
								is_default_billing: values.is_default_billing,
								is_default_shipping: values.is_default_shipping,
							},
							callback: (r) => {
								if (!r.exc) {
									frappe.show_alert({
										message: __("The LANDA Member is now linked as a contact of this Organization and the related Customer"),
										indicator: "green",
									});
									frm.reload_doc();
								}
							},
						});
					}
				);
			});
		}
	},
	onload: function (frm) {
		frm.set_query("public_address", erpnext.queries.address_query);
		frm.set_query("public_contact", erpnext.queries.contact_query);
	},
	update_naming_series: function (frm) {
		frm.call("get_series_current").then((r) => {
			const current = r.message;
			const d = new frappe.ui.Dialog({
				title: __("Update Naming Series"),
				fields: [
					{
						label: "Current",
						fieldname: "current",
						fieldtype: "Int",
						default: current,
					},
				],
				primary_action: function () {
					const data = d.get_values();

					if (data.current === current) {
						d.hide();
						return;
					} else {
						frm.call("set_series_current", { current: data.current }).then((r) => {
							if (!r.exc) {
								frappe.show_alert({
									message: __("Naming Series Updated"),
									indicator: "green",
								});
							}
							d.hide();
						});
					}
				},
				primary_action_label: __("Update"),
			});
			d.show();
		});
	},
});

function disable_map_controls(field) {
	/* disable all map controls except "marker" */
	field.get_leaflet_controls = () =>
		new L.Control.Draw({
			draw: {
				polyline: false,
				polygon: false,
				circle: false,
				circlemarker: false,
				rectangle: false,
			},
			edit: {
				featureGroup: field.editableLayers,
				edit: false,
			},
		});
}
