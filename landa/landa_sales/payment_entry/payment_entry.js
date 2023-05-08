frappe.ui.form.on('Payment Entry', {
    refresh(frm) {
        frm.trigger('set_year_of_settlement');
        frm.trigger('fetch_organization');
    },
    set_year_of_settlement(frm) {
        // Do nothing if year_of_settlement is already set
        if (!frm.doc.year_of_settlement && frm.doc.references) {
            // Get all rows where a Sales Invoice or Sales Order is linked
            const references = frm.doc.references.filter(
                (ref) =>
                    ['Sales Invoice', 'Sales Order'].includes(ref.reference_doctype) &&
                    ref.reference_name
            );
            if (references) {
                // we can only have one year of settlement, therefore we just
                // take it from the first reference
                const ref = references[0];
                frappe.db.get_value(ref.reference_doctype, ref.reference_name, 'year_of_settlement', (message) => {
                    if (message && message.year_of_settlement) {
                        frm.set_value('year_of_settlement', message.year_of_settlement);
                    }
                });
            }
        }
    },
    party_type(frm) {
        frm.trigger('fetch_organization');
    },
    fetch_organization(frm) {
        if (frm.doc.party_type === 'Customer') {
            frm.add_fetch('party', 'organization', 'organization', frm.doctype);
        } else {
            delete frm.fetch_dict[frm.doctype]['organization'];
        }
    },
});


frappe.ui.form.on('Payment Entry Reference', {
    reference_name(frm, cdt, cdn) {
        frm.trigger('set_year_of_settlement');
    }
});
