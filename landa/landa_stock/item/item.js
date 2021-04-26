frappe.ui.form.on("Item", {
    onload: function(frm) {
        if (frm.doc.variant_of && frm.doc.attributes) {
            const row = frm.doc.attributes.filter((row) => row.attribute === 'Gültigkeitsjahr')[0] || {};
            const year_of_validity = row.attribute_value || '';

            if (year_of_validity) {
                // Set "Valid From Year" and "Valid To Year" to year_of_validity from Attribute Value
                frm.set_value('valid_from_year', year_of_validity);
                frm.set_value('valid_to_year', year_of_validity);

                // Make "Valid From Year" and "Valid To Year" read only
                frm.set_df_property('valid_from_year', 'read_only', true);
                frm.set_df_property('valid_to_year', 'read_only', true);
            }
        }
    }
});