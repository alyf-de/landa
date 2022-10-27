// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("LANDA Member", {
    setup: function (frm) {
        // only the leaves of the organiztaion tree can have members
        frm.set_query("organization", function () {
            return {
                filters: {
                    is_group: 0
                }
            };
        });
    },
    refresh: function (frm) {
        // Automatically add the backlink to LANDA Member when a new Address or
        // Contact is added.
        frappe.dynamic_link = {
            doc: frm.doc,
            fieldname: "name",
            doctype: "LANDA Member"
        };

        // Display Address and Contact only after the LANDA Member has been created,
        // not on the initial form.
        frm.toggle_display(["section_address_and_contact"], !frm.doc.__islocal);

        if (frm.doc.__islocal) {
            frappe.contacts.clear_address_and_contact(frm);
        } else {
            frappe.contacts.render_address_and_contact(frm);

            if (frappe.model.can_delete("delete")) {
                frm.page.add_menu_item(__("Delete"), function () {
                    if (frm.doc.user) {
                        const link_to_user = `<a href="/app/user/${frm.doc.user}">${frm.doc.user}</a>`;
                        frappe.throw(__("Please delete User {0} first.", [link_to_user]));
                    }
                    frappe
                        .xcall("landa.utils.preview_delete", { doctype: frm.doc.doctype, name: frm.doc.name })
                        .then(function (prompt_string) {
                            frappe.confirm(prompt_string, function () {
                                frappe.model.delete_doc("LANDA Member", frm.doc.name, function() {
                                    window.history.back();
                                });
                            });
                        });
                });
            }
        }
    },
});
