import frappe


def execute():
	lease_contracts = frappe.get_all("Lease Contract", pluck="name")
	for name in lease_contracts:
		lease_contract = frappe.get_doc("Lease Contract", name)
		rent_per_year = frappe.db.get_value("Lease Contract", name, "rent_per_year")
		lease_contract.lease_contract_rent = []
		lease_contract.append(
			"lease_contract_rent",
			{
				"from_date": lease_contract.start_date,
				"to_date": lease_contract.end_date,
				"rent_per_year": rent_per_year,
			},
		)
		lease_contract.save()
