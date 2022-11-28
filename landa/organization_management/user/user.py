

import frappe
from frappe import _
from frappe.permissions import add_user_permission
from frappe.core.doctype.user.user import User, STANDARD_USERS

from landa.overrides import get_default_company
from landa.organization_management.doctype.member_function.member_function import apply_active_member_functions
from landa.utils import purge_all


def on_update(doc: User, event=None):
	if (not doc.enabled) or (doc.name in STANDARD_USERS):
		return

	if doc.organization and doc.has_value_changed("organization"):
		add_user_permission("Organization", doc.organization, doc.name, ignore_permissions=True)
		add_user_permission("Company", get_default_company(doc.organization), doc.name, ignore_permissions=True)

	if doc.landa_member and doc.has_value_changed("landa_member"):
		# Restrict LANDA Member to itself and it's Organization
		add_user_permission("LANDA Member", doc.landa_member, doc.name, ignore_permissions=True)
		apply_active_member_functions({"member": doc.landa_member})


def validate(doc: User, event=None):
	if (not doc.enabled) or (doc.name in STANDARD_USERS):
		return

	doc.append_roles("LANDA Member")

	if doc.landa_member:
		existing_user = frappe.db.exists(
			"User",
			{
				"landa_member": doc.landa_member,
				"name": ("!=", doc.name),
				"enabled": 1
			}
		)
		if existing_user:
			frappe.throw(
				_("User {0} is already linked to LANDA Member {1}").format(existing_user, doc.landa_member)
			)


def on_trash(user: User, event: str) -> None:
	purge_all("User", user.name)
