# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = "0.0.4"

import frappe


@frappe.whitelist(allow_guest=True)
def complete_setup_wizard_for_ci(site):
	print("Completing Setup Wizard...")
	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

	with frappe.init_site(site):
			frappe.connect()

			if not frappe.get_all("Company", limit=1):
				setup_complete(
					{
						"full_name": "Test User",
						"email": "test_demo@erpnext.com",
						"company_tagline": "Landesverband Sächsischer Angler",
						"password": "demo",
						"fy_start_date": "2023-01-01",
						"fy_end_date": "2023-12-31",
						"bank_account": "Deutsche Bank",
						"domains": ['Non Profit'],
						"company_name": "Landesverband Sächsischer Angler",
						"chart_of_accounts": "SKR04 mit Kontonummern",
						"company_abbr": "LV",
						"currency": "EUR",
						"timezone": "Europe/Berlin",
						"country": "Germany",
						"language": "english",
					}
				)
