from frappe import enqueue


def daily():
	enqueue(
		"landa.organization_management.doctype.member_function.member_function.disable_expired_member_functions",
		queue="long",
	)
	enqueue(
		"landa.water_body_management.doctype.lease_contract.lease_contract.deactivate_lease_contracts",
		queue="long",
	)
	enqueue(
		"landa.water_body_management.doctype.lease_contract.lease_contract.activate_lease_contracts",
		queue="long",
	)
	enqueue(
		"landa.water_body_management.doctype.water_body.water_body.remove_outdated_information",
		queue="long",
	)
	enqueue("landa.organization_management.user.user.delete_or_disable_inactive_users")


def all():
	# probably no longer needed, disabled in hooks
	enqueue(
		"landa.organization_management.address.address.rename_addresses",
		queue="long",
		timeout=250,
		limit=25,
	)
