// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('External Contact', {
    refresh: function(frm) {
        // Automatically add the backlink to External Contact when a new Address or
        // Contact is added.
        frappe.dynamic_link = { doc: frm.doc, fieldname: 'name', doctype: 'External Contact' };

        // Display Address and Contact only after the External Contact has been created,
        // not on the initial form.
        frm.toggle_display(['section_address_and_contact'], !frm.is_new());

        if (frm.is_new()) {
            frappe.contacts.clear_address_and_contact(frm);
        }
        else {
            frappe.contacts.render_address_and_contact(frm);
        }
    },
});
