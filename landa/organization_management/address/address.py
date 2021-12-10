import frappe

from frappe import _
from frappe.utils import cstr
from frappe.model.naming import make_autoname


def autoname(address, event):
	"""
	Copy of Address.autoname, but prefers to use LANDA Member or Organization
	name as Address Title.
	"""
	if address.links:
		for link in address.links:
			if link.link_doctype == "LANDA Member":
				member_names = frappe.get_value(
					"LANDA Member", link.link_name, ["first_name", "last_name"]
				)
				full_name = " ".join(member_names)
				link.link_title = full_name

			for dt, field in (
				("Company", "company_name"),
				("Organization", "organization_name"),
				("Customer", "customer_name"),
			):
				if dt != link.link_doctype:
					continue

				title = frappe.get_value(dt, link.link_name, field)
				link.link_title = title

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
		address.name = (
			cstr(address.address_title).strip() + " - " + cstr(link_name).strip()
		)
		if frappe.db.exists("Address", address.name):
			address.name = make_autoname(address.name + "-.#")
	else:
		frappe.throw(_("Address Title and Links are mandatory."))
