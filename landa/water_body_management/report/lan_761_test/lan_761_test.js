// Copyright (c) 2023, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["LAN-761 Test"] = {
	"filters": [
		{
			"fieldname": "from_year",
			"fieldtype": "Int",
			"label": __("From Year"),
			"mandatory": 0,
			"wildcard_filter": 0,
			"default": moment().year() - 1,
		}

	]
};
