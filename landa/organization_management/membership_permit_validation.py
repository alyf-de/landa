import frappe
from frappe import _


def member_has_active_supporting_membership(member: str, year: int, exclude: str | None = None) -> bool:
	filters: dict = {"member": member, "year": year}
	if exclude:
		filters["name"] = ["!=", exclude]

	return bool(frappe.db.exists("Supporting Membership", filters))


def member_has_active_yearly_fishing_permit(member: str, year: int, exclude: str | None = None) -> bool:
	filters: dict = {
		"member": member,
		"docstatus": 1,
		"year": year,
	}
	if exclude:
		filters["name"] = ["!=", exclude]

	return bool(frappe.db.exists("Yearly Fishing Permit", filters))


def validate_no_active_yearly_fishing_permit(member: str, year: int) -> None:
	if member_has_active_yearly_fishing_permit(member, year):
		frappe.throw(
			_(
				"Member {0} has an active Yearly Fishing Permit. A member cannot have both an active Supporting Membership and an active Yearly Fishing Permit at the same time."
			).format(member)
		)


def validate_no_active_supporting_membership(member: str, year: int) -> None:
	if member_has_active_supporting_membership(member, year):
		frappe.throw(
			_(
				"Member {0} has an active Supporting Membership. A member cannot have both an active Supporting Membership and an active Yearly Fishing Permit at the same time."
			).format(member)
		)
