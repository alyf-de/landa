frappe.ui.form.on("Address", {
	before_save(frm) {
		address_and_contact_before_save(frm);
	},
});

frappe.ui.form.on("Contact", {
	before_save(frm) {
		address_and_contact_before_save(frm);
	},
});

function address_and_contact_before_save(frm) {
	frm.doc.customer = "";
	frm.doc.landa_member = "";
	frm.doc.organization = "";

	frm.doc.links.forEach((link) => {
		if (link["link_doctype"] === "Customer") {
			frm.doc.customer = link["link_name"];
			frm.doc.organization = link["link_name"];
		}

		if (link["link_doctype"] === "Company") {
			frm.doc.organization = link["link_name"];
		}

		if (link["link_doctype"] === "LANDA Member") {
			frm.doc.landa_member = link["link_name"];
			frappe.db
				.get_value("LANDA Member", link["link_name"], "organization")
				.then((r) => {
					frm.doc.organization = r.message.organization;
				});
		}

		if (link["link_doctype"] === "Organization") {
			frm.doc.organization = link["link_name"];
		}

		if (link["link_doctype"] === "External Contact") {
			frappe.db
				.get_value("External Contact", link["link_name"], "organization")
				.then((r) => {
					frm.doc.organization = r.message.organization;
				});
		}
	});
}
