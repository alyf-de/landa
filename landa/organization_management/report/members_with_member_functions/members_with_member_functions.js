// Copyright (c) 2016, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["General Member Function Report"] = {
	"filters": [
        {
            "fieldname": "first_name",
            "fieldtype": "Data",
            "label": __("First Name"),
            "mandatory": 0,
            "wildcard_filter": 0
           },
           {
            "fieldname": "last_name",
            "fieldtype": "Data",
            "label": __("Last Name"),
            "mandatory": 0,
            "wildcard_filter": 0
           },
           {
            "fieldname": "member_function_category",
            "fieldtype": "Link",
            "options": "Member Function Category",
            "label": __("Member Function Category"),
            "mandatory": 0,
            "wildcard_filter": 0
           },
           {
            "fieldname": "organization",
            "fieldtype": "Link",
            "options": "Organization",
            "label": __("Organization"),
            "mandatory": 0,
            "wildcard_filter": 0,
            "default": frappe.defaults.get_user_default("Organization"),
           }

	]
};