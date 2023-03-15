def daily():
	from landa.organization_management.doctype.member_function.member_function import (
		disable_expired_member_functions,
	)
	from landa.water_body_management.doctype.lease_contract.lease_contract import (
		disable_expired_lease_contracts,
	)

	disable_expired_member_functions()
	disable_expired_lease_contracts()
