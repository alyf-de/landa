// Copyright (c) 2022, Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Members in Water Body Management"] = {
	"filters": [
           {
            "fieldname": "water_body",
            "fieldtype": "Link",
            "options": "Water Body",
            "label": __("Water Body"),
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
           },
		   {
            "fieldname": "fishing_area",
            "fieldtype": "Link",
            "options": "Fishing Area",
            "label": __("Fishing Area"),
            "mandatory": 0,
            "wildcard_filter": 0
           }
	]
};
