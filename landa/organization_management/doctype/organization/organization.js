// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Organization", {
	setup: function (frm) {
		disable_map_controls(frm.fields_dict["location"]);

		frm.make_methods = {
			"Sales Order": () => frm.trigger("create_sales_order"),
			"Sales Invoice": () => frm.trigger("create_sales_invoice"),
			"Delivery Note": () => frm.trigger("create_delivery_note"),
			"Payment Entry": () => frm.trigger("create_payment_entry"),
		};
	},
	onload: function (frm) {
		frm.trigger("set_fishing_area_query");
		frm.set_query("public_address", erpnext.queries.address_query);
		frm.set_query("public_contact", erpnext.queries.contact_query);
	},
	set_fishing_area_query: function (frm) {
		if (
			!frm.doc.parent_organization ||
			frm.doc.parent_organization === frappe.boot.landa.state_organization
		) {
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
		frm._expected_work_hours_edited = false;

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
			frm.trigger("render_member_functions");
		}

		if (frappe.user.has_role("System Manager") && !frm.is_dirty()) {
			frm.page.add_menu_item(__("Update Naming Series"), () =>
				frm.trigger("update_naming_series"),
			);
		}

		if (!frm.is_dirty() && frm.has_perm("write")) {
			frm.page.add_menu_item(__("Link Member as Contact"), () =>
				prompt_link_member_as_contact(frm),
			);
		}

		if (!frm.is_new() && frappe.model.can_read("Sales Invoice")) {
			frm.add_custom_button(__("Billing History"), () => {
				frappe.set_route("query-report", "Billing History", {
					organization: frm.doc.name,
				});
			});
		}
	},
	expected_work_hours_per_year(frm) {
		frm._expected_work_hours_edited = true;
	},
	before_save(frm) {
		if (!frm._expected_work_hours_edited) {
			return;
		}

		return new Promise((resolve, reject) => {
			frappe.confirm(
				__(
					"Changing Expected Work Hours per Year will create Work Ledger Entries for all members of this organization. Do you want to continue?",
				),
				() => resolve(),
				() => {
					frappe.validated = false;
					reject();
				},
			);
		});
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
	create_sales_order: function (frm) {
		frappe.new_doc("Sales Order", {
			...get_basic_sales_data(frm.doc),
			year_of_settlement: landa.utils.get_default_year(),
		});
	},
	create_sales_invoice: function (frm) {
		frappe.new_doc("Sales Invoice", get_basic_sales_data(frm.doc));
	},
	create_delivery_note: function (frm) {
		frappe.new_doc("Delivery Note", get_basic_sales_data(frm.doc));
	},
	create_payment_entry: function (frm) {
		frappe.model.open_mapped_doc({
			method: "landa.organization_management.doctype.organization.organization.make_payment_entry",
			frm: frm,
		});
	},
	render_member_functions: function (frm) {
		const member_functions = (frm.doc.__onload || {}).active_member_functions || [];
		frm.fields_dict.member_functions.wrapper.innerHTML = landa.utils.render_static_grid({
			id: "organization_member_functions_grid",
			label: __("Member Functions"),
			data: member_functions,
			columns: get_organization_member_function_columns(),
		});
	},
});

function prompt_link_member_as_contact(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Link Member as Contact"),
		fields: [
			{
				fieldname: "landa_member",
				label: __("LANDA Member"),
				fieldtype: "Link",
				options: "LANDA Member",
				reqd: 1,
				onchange() {
					fill_single_address_and_contact(this.layout);
				},
				get_query() {
					return {
						query: "landa.organization_management.doctype.organization.organization.member_with_address_and_contact_query",
						filters: {
							organization: frm.doc.name,
						},
					};
				},
			},
			{
				fieldname: "contact",
				label: __("Contact"),
				fieldtype: "Link",
				options: "Contact",
				reqd: 1,
				depends_on: "eval:doc.landa_member",
				get_query() {
					return member_link_query(
						"frappe.contacts.doctype.contact.contact.contact_query",
						dialog.get_value("landa_member"),
					);
				},
			},
			{
				fieldname: "address",
				label: __("Address"),
				fieldtype: "Link",
				options: "Address",
				reqd: 1,
				depends_on: "eval:doc.landa_member",
				get_query() {
					return member_link_query(
						"frappe.contacts.doctype.address.address.address_query",
						dialog.get_value("landa_member"),
						{ disabled: 0 },
					);
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
		primary_action(values) {
			dialog.hide();
			frm.call({
				method: "link_contact",
				doc: frm.doc,
				freeze: true,
				freeze_message: __("Linking Contact ..."),
				args: {
					landa_member: values.landa_member,
					contact: values.contact,
					address: values.address,
					is_default_billing: values.is_default_billing,
					is_default_shipping: values.is_default_shipping,
				},
				callback: (r) => {
					if (!r.exc) {
						frappe.show_alert({
							message: __(
								"The LANDA Member is now linked as a contact of this Organization and the related Customer",
							),
							indicator: "green",
						});
						frm.reload_doc();
					}
				},
			});
		},
	});
	dialog.show();
}

function member_link_query(query, landa_member, filters = {}) {
	return {
		query,
		filters: {
			link_doctype: "LANDA Member",
			link_name: landa_member || "",
			...filters,
		},
	};
}

function fill_single_address_and_contact(dialog) {
	const member = dialog.get_value("landa_member");
	const request_id = (dialog._member_link_request || 0) + 1;
	dialog._member_link_request = request_id;

	frappe.run_serially([
		() => dialog.set_value("contact", ""),
		() => dialog.set_value("address", ""),
		() => {
			if (!member || dialog._member_link_request !== request_id) {
				return;
			}

			return frappe
				.call({
					method: "landa.organization_management.doctype.organization.organization.get_single_address_and_contact",
					args: { landa_member: member },
				})
				.then((r) => {
					if (dialog._member_link_request !== request_id) {
						return;
					}

					const values = r.message || {};
					return frappe.run_serially([
						() => values.contact && dialog.set_value("contact", values.contact),
						() => values.address && dialog.set_value("address", values.address),
					]);
				});
		},
	]);
}

function get_organization_member_function_columns() {
	return [
		{
			fieldname: "member_function_category",
			label: __("Function"),
			fieldtype: "Link",
			width: 4,
			route: (row) => ["member-function", row.name],
		},
		{
			fieldname: "member",
			label: __("Member"),
			fieldtype: "Link",
			width: 5,
			value: (row) =>
				[row.member_first_name, row.member_last_name].filter(Boolean).join(" ") ||
				row.member,
			route: (row) => ["landa-member", row.member],
		},
		{
			fieldname: "start_date",
			label: __("Since"),
			fieldtype: "Date",
			width: 3,
			formatter: (value) => (value ? frappe.datetime.str_to_user(value) : ""),
		},
	];
}

/**
 * Get the basic data for a sales document
 * @param {Object} doc - The organization document
 * @returns {Object} - The basic data for a sales document
 */
function get_basic_sales_data(doc) {
	return {
		organization: doc.name,
		customer: doc.name,
		company: frappe.boot.landa.company,
		year_of_settlement: new Date().getFullYear(),
	};
}

function disable_map_controls(field) {
	/* disable all map controls except "marker" */
	field.get_leaflet_controls = () =>
		new window.L.Control.Draw({
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
