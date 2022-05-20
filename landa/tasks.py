def daily():
	from landa.organization_management.doctype.member_function.member_function import (
		disable_expired_member_functions,
	)
	from landa.water_body_management.doctype.lease_contract.lease_contract import (
		disable_expired_lease_contracts,
	)

	disable_expired_member_functions()
	disable_expired_lease_contracts()


def all():
	from frappe import enqueue

	# probably no longer needed, disabled in hooks
	enqueue(
		"landa.organization_management.address.address.rename_addresses",
		queue="long",
		timeout=250,
		limit=25,
	)
