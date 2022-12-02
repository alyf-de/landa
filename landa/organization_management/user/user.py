

import frappe
from frappe import _
from frappe.permissions import add_user_permission
from frappe.core.doctype.user.user import User, STANDARD_USERS

from landa.overrides import get_default_company
from landa.organization_management.doctype.member_function.member_function import (
	apply_active_member_functions,
)
from landa.utils import purge_all


def validate(doc: User, event=None):
	if (not doc.enabled) or (doc.name in STANDARD_USERS):
		return

	doc.append_roles("LANDA Member")

	if doc.landa_member:
		existing_user = frappe.db.exists(
			"User",
			{"landa_member": doc.landa_member, "name": ("!=", doc.name), "enabled": 1},
		)
		if existing_user:
			frappe.throw(
				_("User {0} is already linked to LANDA Member {1}").format(
					existing_user, doc.landa_member
				)
			)


def after_insert(doc: User, event=None):
	if (not doc.enabled) or (doc.name in STANDARD_USERS):
		return

	if doc.organization:
		restrict_to_organization(doc.organization, doc.name)

	if doc.landa_member:
		restrict_to_member(doc.landa_member, doc.name)


def on_update(doc: User, event=None):
	if (not doc.enabled) or (doc.name in STANDARD_USERS):
		return

	if doc.organization and doc.has_value_changed("organization"):
		restrict_to_organization(doc.organization, doc.name)

	if doc.landa_member and doc.has_value_changed("landa_member"):
		restrict_to_member(doc.landa_member, doc.name)


def restrict_to_organization(organization: str, user: str) -> None:
	add_user_permission("Organization", organization, user, ignore_permissions=True)
	add_user_permission(
		"Company", get_default_company(organization), user, ignore_permissions=True
	)


def restrict_to_member(member: str, user: str) -> None:
	add_user_permission("LANDA Member", member, user, ignore_permissions=True)
	apply_active_member_functions({"member": member})


def on_trash(user: User, event: str) -> None:
	purge_all("User", user.name)