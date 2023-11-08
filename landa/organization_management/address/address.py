import frappe
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils import cstr


def autoname(address, event):
	"""
	Copy of Address.autoname, but prefers to use LANDA Member or Organization
	name as Address Title.
	"""
	link_name = None
	if address.links:
		for link in address.links:
			if link.link_doctype == "LANDA Member":
				link.link_title = " ".join(
					frappe.get_value("LANDA Member", link.link_name, ["first_name", "last_name"])
				)

			if link.link_doctype == "External Contact":
				link.link_title = " ".join(
					frappe.get_value("External Contact", link.link_name, ["first_name", "last_name"])
				)

			for dt, field in (
				("Company", "company_name"),
				("Organization", "organization_name"),
				("Customer", "customer_name"),
			):
				if dt != link.link_doctype:
					continue

				link.link_title = frappe.get_value(dt, link.link_name, field)

		# Prefer the member's name as address title otherwise, use any link title as address title
		for link in address.links:
			address.address_title = link.link_title

			if link.link_doctype == "Company":
				link_name = frappe.get_value("Company", link.link_name, "abbr")
			else:
				link_name = link.link_name

			if link.link_doctype == "LANDA Member":
				break

		if not address.address_title:
			address.address_title = address.links[0].link_title

	if address.address_title and link_name:
		address.name = cstr(address.address_title).strip() + " - " + cstr(link_name).strip()
		if frappe.db.exists("Address", address.name):
			address.name = make_autoname(address.name + "-.#")
	else:
		frappe.throw(_("Address Title and Links are mandatory."))


def rename_addresses(limit: int):
	doctype = "Address"
	address_names = frappe.get_all(
		doctype,
		filters=[
			["Dynamic Link", "link_name", "is", "set"],
			["Address", "name", "like", "% - Pers%"],
		],
		limit=limit,
		pluck="name",
	)

	for old_name in address_names:
		if not frappe.db.exists(doctype, old_name):
			continue

		doc = frappe.get_doc(doctype, old_name)

		try:
			autoname(doc, None)  # changes doc.name to the new name
		except frappe.exceptions.ValidationError:
			continue

		new_name = doc.name

		if new_name[-2:] == "-1":
			new_name = new_name[:-2]

		if old_name == new_name:
			continue

		try:
			frappe.rename_doc(
				doctype,
				old_name,
				new_name,
				ignore_permissions=True,  # checking permissions takes too long
				ignore_if_exists=True,  # don't rename if a record with the same name exists already
				show_alert=False,  # no need to show a UI alert, we're in the console
				rebuild_search=False,  # we do that explicitly at the end
			)
		except frappe.exceptions.ValidationError:
			continue

		frappe.db.commit()

	frappe.enqueue("frappe.utils.global_search.rebuild_for_doctype", doctype=doctype)


@frappe.whitelist()
def get_address_display(address_dict):
	"""Overwrite frappe.contacts.doctype.address.address.get_address_display

	Changes: Siltenly return None if the user does not have permission to view the address.
	        This is necessary because users don't have permission to access records from their
	        regional organization, but its address is still fetched in the sales workflow.
	"""
	from frappe.contacts.doctype.address.address import render_address

	check_permissions = True
	if isinstance(address_dict, str):
		address = frappe.get_cached_doc("Address", address_dict)
		if belongs_to_regional_org(address):
			check_permissions = False

	return render_address(address_dict, check_permissions=check_permissions)


def belongs_to_regional_org(address):
	"""Check if an address belongs to a regional organization."""
	if not address.links:
		return False

	for link in address.links:
		if link.link_doctype == "Organization" and link.link_name in ("AVE", "AVL", "AVS"):
			return True

	return False
