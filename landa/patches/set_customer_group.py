import frappe


def execute():
	customer = frappe.qb.DocType("Customer")
	(
		frappe.qb.update(customer)
		.set(customer.customer_group, "Non Profit")
		.where(customer.customer_group == "All Customer Groups")
	).run()
