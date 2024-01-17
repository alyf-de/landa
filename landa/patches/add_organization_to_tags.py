import frappe
from frappe.modules.utils import sync_customizations

from landa.utils import get_member_and_organization


def execute():
	"""Add organization to tags"""
	# make sure Tag Organization is available
	frappe.reload_doc("organization_management", "doctype", "tag_organization")

	# make sure Tag is customized
	sync_customizations("landa")

	tags = frappe.get_all("Tag", fields=["name", "owner"])

	for tag in tags:
		owner_organization = get_member_and_organization(tag["owner"])[1]

		if owner_organization:
			tag_doc = frappe.get_doc("Tag", tag["name"])

			if all(org.organization != owner_organization for org in tag_doc.get("organizations", [])):
				tag_doc.append("organizations", {"organization": owner_organization})
				tag_doc.save(ignore_permissions=True)
