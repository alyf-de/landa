// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Water Body", {
	refresh: function (frm) {
		if (
			!frm.is_new() &&
			frappe.boot.landa.regional_organization &&
			frm.doc.organization !== frappe.boot.landa.regional_organization
		) {
			frm.disable_form();
		}
		bind_rotation_event(frm);
		frm.set_query(
			"icon",
			function (doc) {
				return {
					filters: {
						icon: ["is", "set"]
					},
				};
			}
		);
	},
	icon: function (frm) {
		if (frm.doc.icon) {
			bind_rotation_event(frm);
		}
	},
});

function bind_rotation_event(frm) {
	const icon_rotation = document.getElementById("icon_rotation");
	const icon_preview = frm.fields_dict.icon_preview.wrapper.getElementsByTagName("img")[0];
	icon_rotation.addEventListener(
		"input",
		function (evt) {
			icon_preview.style.transform = `rotate(${evt.target.value}deg)`;
			frm.rotation_angle = evt.target.value;
		}
	);
}
