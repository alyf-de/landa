
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
			if link.link_doctype == "Organization":
				organization_name = frappe.get_value("Organization", link.link_name, "organization_name")
				address.address_title = organization_name
				link.link_title = organization_name

			if link.link_doctype == "Customer":
				customer_name = frappe.get_value("Customer", link.link_name, "customer_name")
				address.address_title = customer_name
				link.link_title = customer_name

			if link.link_doctype == "LANDA Member":
				member_names = frappe.get_value("LANDA Member", link.link_name, ["first_name", "last_name"])
				full_name = " ".join(member_names)
				address.address_title = full_name
				link.link_title = full_name

		if not address.address_title:
			address.address_title = address.links[0].link_title

	if address.address_title:
		address.name = (cstr(address.address_title).strip() + " - " + cstr(_(address.address_type)).strip())
		if frappe.db.exists("Address", address.name):
			address.name = make_autoname(address.name + "-.#")
	else:
		frappe.throw(_("Address Title is mandatory."))
