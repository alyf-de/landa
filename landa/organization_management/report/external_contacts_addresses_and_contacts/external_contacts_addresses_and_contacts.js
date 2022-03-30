// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["External Contacts Addresses and Contacts"] = {
    filters: [
        {
            fieldname: "organization",
            fieldtype: "Link",
            options: "Organization",
            label: __("Organization"),
            mandatory: 0,
            wildcard_filter: 0,
            default: frappe.defaults.get_user_default("Organization"),
        },
        {
            fieldname: "is_magazine_recipient",
            fieldtype: "Check",
            label: __("Is Magazine Recipient"),
            mandatory: 0,
            wildcard_filter: 0,
        },
    ],
};
