def daily():
	from landa.organization_management.doctype.member_function.member_function import (
		disable_expired_member_functions,
	)
	from landa.water_body_management.doctype.lease_contract.lease_contract import (
		disable_expired_lease_contracts,
	)
	from landa.water_body_management.doctype.water_body.water_body import remove_outdated_information

	disable_expired_member_functions()
	disable_expired_lease_contracts()
	remove_outdated_information()


def all():
	from frappe import enqueue

	# probably no longer needed, disabled in hooks
	enqueue(
		"landa.organization_management.address.address.rename_addresses",
		queue="long",
		timeout=250,
		limit=25,
	)
