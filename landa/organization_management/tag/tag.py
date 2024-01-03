# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe

from landa.utils import get_current_member_data


def has_permission(doc, user):
	if not user:
		user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return True

	allowed_organizations = frappe.get_all(
		"User Permission", filters={"user": user, "allow": "Organization"}, pluck="for_value"
	)

	if any(org.organization in allowed_organizations for org in doc.get("organizations")):
		return True

	return False


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return None

	return """exists (
                select 1 from `tabTag Organization`
                where
                    `tabTag Organization`.parent = `tabTag`.name and
                    `tabTag Organization`.organization in (
                        select for_value
                        from `tabUser Permission`
                        where `allow` = 'Organization'
                        and `user` = {user}
                    )
              )""".format(
		user=frappe.db.escape(user)
	)


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

	return frappe.desk.doctype.tag.tag.add_tag(tag, dt, dn, color)
