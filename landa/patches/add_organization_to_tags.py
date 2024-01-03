import frappe

from landa.utils import get_member_and_organization


def execute():
	tags = frappe.get_all("Tag", fields=["name", "owner"])

	for tag in tags:
		owner_organization = get_member_and_organization(tag["owner"])[1]

		if owner_organization:
			tag_doc = frappe.get_doc("Tag", tag["name"])

			if not any(org.organization == owner_organization for org in tag_doc.get("organizations")):
				tag_doc.append("organizations", {"organization": owner_organization})
				tag_doc.save(ignore_permissions=True)
