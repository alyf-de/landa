// Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LANDA Member Count"] = {
	"filters": [
		{
			"fieldname": "organization",
			"fieldtype": "Link",
			"label": __("Organization"),
			"mandatory": 1,
			"options": "Organization",
			"wildcard_filter": 0,
			"default": frappe.defaults.get_user_default("Organization"),
			"get_query": function() {
				return {
					filters: [
						["Organization", "parent_organization", "in", ["LV", "AVL", "AVS", "AVE"]]
					]
				}
			}
		},
		{
			"fieldname": "year_of_settlement",
			"fieldtype": "Data",
			"label": __("Year of Settlement"),
			"mandatory": 0,
			"wildcard_filter": 0,
			"default": new Date().getFullYear()
		},
		{
			"fieldname": "beitragsart",
			"fieldtype": "Select",
			"label": __("Beitragsart"),
			"mandatory": 0,
			"options": "\nVollzahler\nFördermitglied\nJugend\nAustauschmarke",
			"wildcard_filter": 0,
		}
	]
};