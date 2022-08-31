frappe.provide("landa");

landa.prefill_items = function (frm) {
    if (!frm.doc.customer || !frm.doc.year_of_settlement) {
        frm.clear_table("items");
        frm.refresh_field("items");
        return;
    }

    return frappe.xcall(
        "erpnext.controllers.queries.item_query", // Use item query to get all selectable items
        {
            doctype: "Item",
            txt: "", // empty search text returns all items
            searchfield: "name",
            start: 0,
            page_len: 99, // limit pre-filled items to 100
            filters: frm.fields_dict["items"].grid.get_field("item_code").get_query(frm.doc).filters, // get existing query filters
            as_dict: true
        },
    ).then((items) => {
            frm.clear_table("items");
            frm.refresh_field("items");

            for (const item of items) {
                const row = frm.add_child("items");
                frappe.model.set_value(row.doctype, row.name, "item_code", item.name);

                // `ControlLink.validate()` does not get triggered by `frappe.model.set_value`,
                // therefore we have to set the "fetch from"-fields manually.
                frappe.model.set_value(row.doctype, row.name, "cannot_be_returned", item.cannot_be_returned);
            }
        }
    );
};
