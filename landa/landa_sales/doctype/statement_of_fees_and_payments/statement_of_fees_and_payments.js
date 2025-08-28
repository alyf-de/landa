// Copyright (c) 2024, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Statement of Fees and Payments", {
	setup(frm) {
		frm.set_query("billing_address", (doc) => {
			return {
				filters: [
					["Dynamic Link", "link_doctype", "=", "Customer"],
					["Dynamic Link", "link_name", "=", doc.customer],
				],
			};
		});

		frm.set_query("billing_contact", (doc) => {
			return {
				filters: [
					["Dynamic Link", "link_doctype", "=", "Customer"],
					["Dynamic Link", "link_name", "=", doc.customer],
				],
			};
		});

		frm.set_query("company_address", (doc) => {
			return {
				filters: [
					["Dynamic Link", "link_doctype", "=", "Company"],
					["Dynamic Link", "link_name", "=", doc.company],
				],
			};
		});

		frm.set_query("payment_entry", "payments", (doc) => {
			return {
				filters: {
					company: doc.company,
					year_of_settlement: doc.year_of_settlement,
					party_type: "Customer",
					party: doc.customer,
					docstatus: 1,
				},
			};
		});
	},

	refresh(frm) {
		if (frm.is_new() && !frm.doc.year_of_settlement) {
			frm.set_value("year_of_settlement", new Date().getFullYear() - 1);
		}
	},

	async company(frm) {
		if (frm.doc.company) {
			const default_address = await frappe.xcall(
				"erpnext.setup.doctype.company.company.get_default_company_address",
				{ name: frm.doc.company, existing_address: frm.doc.company_address || "" }
			);

			if (default_address) {
				frm.set_value("company_address", default_address);
			} else {
				frm.set_value("company_address", "");
			}
		}
	},

	billing_address(frm) {
		erpnext.utils.get_address_display(frm, "billing_address", "billing_address_display");
	},

	company_address(frm) {
		erpnext.utils.get_address_display(frm, "company_address", "company_address_display");
	},
});