// Copyright (c) 2016, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Current Member Data"] = {
    "filters": [
        {
            "fieldname": "organization",
            "fieldtype": "Link",
            "options": "Organization",
            "label": __("Organization"),
            "mandatory": 0,
            "wildcard_filter": 0,
            "default": frappe.defaults.get_user_default("Organization"),
        },
    ],
    onload: function (query_report) {
        const b = cur_page.page.page.wrapper.find(".sub-heading");
        b.html(`
            Sehen Sie sich bitte unbedingt vor der ersten Benutzung <a href="/how-to/Mitgliedsdatenimport" target=_blank style="color: blue;">diese Anleitung</a> an.</p>
        </div>`).toggleClass("hide", false);
    }
};
