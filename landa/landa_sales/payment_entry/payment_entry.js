frappe.ui.form.on("Payment Entry", {
	onload(frm) {
		// If the Payment Entry was created from a Sales Invoice, the party is
		// already set, but did not trigger the "fetch from". We need to do this
		// manually.
		if (!frm.is_new()) {
			return;
		}

		if (frm.doc.party_type === "Customer" && frm.doc.party && !frm.doc.organization) {
			// Validating the 'party' link field will trigger it's "fetch from".
			frm.fields_dict.party.validate(frm.doc.party);
		}
	},
	refresh(frm) {
		frm.trigger("set_year_of_settlement");

		if (frm.is_new()) {
			landa.utils.set_company_and_customer(frm, "company", "party");
		}

		frm.remove_custom_button(__("Ledger"));
		frm.remove_custom_button(__("UnReconcile"), __("Actions"));
	},
	set_year_of_settlement(frm) {
		// Do nothing if year_of_settlement is already set
		if (!frm.doc.year_of_settlement && frm.doc.references) {
			// Get all rows where a Sales Invoice or Sales Order is linked
			const references = frm.doc.references.filter(
				(ref) =>
					["Sales Invoice", "Sales Order"].includes(ref.reference_doctype) &&
					ref.reference_name
			);
			if (references) {
				// we can only have one year of settlement, therefore we just
				// take it from the first reference
				const ref = references[0];
				frappe.db.get_value(
					ref.reference_doctype,
					ref.reference_name,
					"year_of_settlement",
					(message) => {
						if (message && message.year_of_settlement) {
							frm.set_value("year_of_settlement", message.year_of_settlement);
						}
					}
				);
			}
		}
	},
	async custom_get_outstanding_invoices(frm) {
		frm.clear_table("references");

		const invoices = await frappe.db.get_list("Sales Invoice", {
			filters: {
				company: frm.doc.company,
				customer: frm.doc.party,
				outstanding_amount: [">", 0.01],
				year_of_settlement: frm.doc.year_of_settlement,
			},
			fields: ["name", "grand_total", "outstanding_amount", "due_date"],
			order_by: "due_date asc",
		});

		let allocated_amount = frm.doc.paid_amount;
		for (const invoice of invoices) {
			frm.add_child("references", {
				reference_doctype: "Sales Invoice",
				reference_name: invoice.name,
				total_amount: invoice.grand_total,
				outstanding_amount: invoice.outstanding_amount,
				allocated_amount: Math.min(invoice.outstanding_amount, allocated_amount > 0 ? allocated_amount : 0),
				due_date: invoice.due_date,
			});
			allocated_amount -= invoice.outstanding_amount;
		}
		frm.refresh_field("references");
	},
});

frappe.ui.form.on("Payment Entry Reference", {
	reference_name(frm, cdt, cdn) {
		frm.trigger("set_year_of_settlement");
	},
});
