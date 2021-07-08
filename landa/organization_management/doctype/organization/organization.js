// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Organization', {
    refresh: function(frm) {
        // Automatically add the backlink to Organization when a new Address or
        // Contact is added.
        frappe.dynamic_link = { doc: frm.doc, fieldname: 'name', doctype: 'Organization' };

        // Display Address and Contact only after the Member has been created,
        // not on the initial form.
        frm.toggle_display(['section_address_and_contact'], !frm.doc.__islocal);

        if (frm.doc.__islocal) {
            frappe.contacts.clear_address_and_contact(frm);
        }
        else {
            frappe.contacts.render_address_and_contact(frm);
        }

        if (frappe.user_roles.includes("System Manager") && !frm.is_new()) {
            frm.page.add_menu_item(__('Update Naming Series'), () => frm.trigger('update_naming_series'));
        }
    },
    update_naming_series: function(frm) {
        frm.call('get_series_current').then((r) => {
            const current = r.message;
            const d = new frappe.ui.Dialog({
                title: __('Update Naming Series'),
                fields: [
                    {
                        "label": "Current",
                        "fieldname": "current",
                        "fieldtype": "Int",
                        "default": current
                    }
                ],
                primary_action: function() {
                    const data = d.get_values();

                    if(data.current === current) {
                        d.hide();
                        return;
                    } else {
                        frm.call('set_series_current', { current: data.current }).then(r => {
                            if (!r.exc) {
                                frappe.show_alert({
                                    message: __('Naming Series Updated'),
                                    indicator: 'green'
                                });
                            }
                            d.hide();
                        });
                    }
                },
                primary_action_label: __('Update')
            });
            d.show();
        });
    },
});
