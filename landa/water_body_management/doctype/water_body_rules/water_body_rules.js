// Copyright (c) 2023, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Water Body Rules", {
	refresh: function (frm) {
		frm.add_custom_button(__("Toggle HTML"), function () {
			frm.trigger("toggle_html");
		});
	},
	toggle_html: function (frm) {
		for (let fieldname of ["water_body_rules", "privacy_policy", "imprint"]) {
			let df = frm.fields_dict[fieldname].df;

			// overwrites Code formatter defined in apps/frappe/frappe/public/js/frappe/form/formatters.js
			df.formatter = df.read_only ? undefined : format_html;
			frm.set_df_property(fieldname, "fieldtype", df.read_only ? "HTML Editor" : "Code");
			frm.set_df_property(fieldname, "options", df.read_only ? "" : "HTML");
			frm.set_df_property(fieldname, "read_only", !df.read_only);
		}
	}
});

// modifies Code formatter defined in apps/frappe/frappe/public/js/frappe/form/formatters.js
// to pretty print HTML
function format_html(value, df) {
	const _value = df.options == "HTML" ? html_beautify(value) : value;
	return "<pre>" + (_value == null ? "" : $("<div>").text(_value).html()) + "</pre>";
}
