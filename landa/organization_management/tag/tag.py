# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.user_permission.user_permission import get_permitted_documents
from frappe.desk.doctype.tag.tag import add_tag as frappe_add_tag

from landa.utils import get_current_member_data


def has_permission(doc, user):
	if not user:
		user = frappe.session.user

	user_roles = frappe.get_roles(user)

	if "System Manager" in user_roles or "LANDA State Organization Employee" in user_roles:
		return True

	if any(
		org.organization in get_permitted_documents("Organization") for org in doc.get("organizations")
	):
		return True

	return False


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	user_roles = frappe.get_roles(user)

	if "System Manager" in user_roles or "LANDA State Organization Employee" in user_roles:
		return None

	permitted_organizations = ", ".join(f"'{org}'" for org in get_permitted_documents("Organization"))

	return f"""exists (
				select 1 from `tabTag Organization`
				where
					`tabTag Organization`.parent = `tabTag`.name and
					`tabTag Organization`.organization in ({permitted_organizations})
			)"""


def before_insert(doc, method):
	doc.append("organizations", {"organization": get_current_member_data().get("organization")})


@frappe.whitelist()
def add_tag(tag, dt, dn, color=None):
	organization = get_current_member_data().get("organization")

	if organization and frappe.db.exists("Tag", tag):
		tag_doc = frappe.get_doc("Tag", tag)

		if organization not in [org.organization for org in tag_doc.organizations]:
			tag_doc.append("organizations", {"organization": organization})
			tag_doc.save(ignore_permissions=True)

	return frappe_add_tag(tag, dt, dn, color)
