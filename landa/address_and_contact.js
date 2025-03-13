for (const dt of ["Contact", "Address"]) {
	frappe.ui.form.on(dt, {
		refresh(frm) {
			if (frm.is_new() && frm.doc.links.length > 0) {
				// This is required when the table row is added via dynamic link,
				// instead of manually.
				frm.trigger("link_name", "Dynamic Link", frm.doc.links[0].name);
			}
		}
	});
}

frappe.ui.form.on("Dynamic Link", {
	link_name(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.link_name) {
			return;
		}

		if (row["link_doctype"] === "Customer") {
			frappe.db.get_value("Customer", row["link_name"], "organization").then((r) => {
				set_organization(frm, r.message.organization);
			});
		}

		if (row["link_doctype"] === "Supplier") {
			frappe.db.get_value("Supplier", row["link_name"], "organization").then((r) => {
				set_organization(frm, r.message.organization);
			});
		}

		if (row["link_doctype"] === "LANDA Member") {
			frappe.db.get_value("LANDA Member", row["link_name"], "organization").then((r) => {
				set_organization(frm, r.message.organization);
			});
		}

		if (row["link_doctype"] === "Organization") {
			set_organization(frm, row["link_name"]);
		}

		if (row["link_doctype"] === "External Contact") {
			frappe.db.get_value("External Contact", row["link_name"], "organization").then((r) => {
				set_organization(frm, r.message.organization);
			});
		}
	},
});

function set_organization(frm, organization) {
	if (!organization || frm.doc.organization === organization) {
		return;
	}

	frm.set_value("organization", organization);
}
