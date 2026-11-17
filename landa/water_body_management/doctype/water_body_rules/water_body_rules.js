// Copyright (c) 2023, ALYF GmbH and contributors
// For license information, please see license.txt

const HTML_FIELDS = ["water_body_rules", "privacy_policy", "imprint"];
const formatted_html = new Map();

let html_formatter;
let toggle_in_progress = false;

frappe.ui.form.on("Water Body Rules", {
	refresh(frm) {
		frm.add_custom_button(__("Toggle HTML"), () => {
			toggle_html(frm);
		});
	},
});

async function toggle_html(frm) {
	if (toggle_in_progress) {
		return;
	}

	toggle_in_progress = true;
	try {
		const show_source = HTML_FIELDS.filter(
			(fieldname) => !frm.fields_dict[fieldname].df.read_only,
		);
		if (show_source.length) {
			html_formatter ??= frappe.require("html_format.bundle.js");
			await html_formatter;
			await Promise.all(
				show_source.map((fieldname) => remember_formatted_html(frm.doc[fieldname])),
			);
		}

		for (const fieldname of HTML_FIELDS) {
			const df = frm.fields_dict[fieldname].df;
			const next_read_only = !df.read_only;

			// Replaces the Code formatter in frappe/form/formatters.js.
			// frappe.format does not await, so the formatted HTML is cached above.
			df.formatter = next_read_only ? format_html : undefined;
			frm.set_df_property(fieldname, "fieldtype", next_read_only ? "Code" : "HTML Editor");
			frm.set_df_property(fieldname, "options", next_read_only ? "HTML" : "");
			frm.set_df_property(fieldname, "read_only", next_read_only);
		}
	} finally {
		toggle_in_progress = false;
	}
}

async function remember_formatted_html(value) {
	if (!value || formatted_html.has(value)) {
		return;
	}

	try {
		formatted_html.set(value, await window.format_html_source(value));
	} catch {
		formatted_html.set(value, value);
	}
}

function format_html(value, df) {
	const source = df.options == "HTML" ? formatted_html.get(value) || value : value;
	return "<pre>" + (source == null ? "" : $("<div>").text(source).html()) + "</pre>";
}
