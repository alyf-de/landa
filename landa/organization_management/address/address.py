import frappe

from frappe import _
from frappe.utils import cstr
from frappe.model.naming import make_autoname


def autoname(address, event):
	"""
	Copy of Address.autoname, but prefers to use LANDA Member or Organization
	name as Address Title.
	"""
	set_address_title(address, event)
	link_name = address.landa_member or address.external_contact or address.organization

	if address.address_title and link_name:
		address.name = (
			f"{cstr(address.address_title).strip()} - {cstr(link_name).strip()}"
		)
		if frappe.db.exists("Address", address.name):
			address.name = make_autoname(f"{address.name}-.#")
	else:
		frappe.throw(_("Address Title and Links are mandatory."))


def set_address_title(address, event):
	if address.landa_member:
		address.address_title = " ".join(
			frappe.get_value(
				"LANDA Member", address.landa_member, ["first_name", "last_name"]
			)
		)
	elif address.external_contact:
		address.address_title = " ".join(
			frappe.get_value(
				"External Contact",
				address.external_contact,
				["first_name", "last_name"],
			)
		)
	elif address.organization:
		address.address_title = frappe.get_value(
			"Organization", address.organization, "organization_name"
		)
