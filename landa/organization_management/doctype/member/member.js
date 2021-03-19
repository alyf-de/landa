// Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Member', {
    setup: function(frm) {
        // only the leaves of the organiztaion tree can have members
        frm.set_query("organization", function() {
            return {
                filters: {
                    'is_group': 0
                }
            };
        });
    },
});
