import frappe

from frappe import _
from frappe.utils import cstr
from frappe.model.naming import make_autoname


def autoname(address, event):
	"""
	Copy of Address.autoname, but prefers to use LANDA Member or Organization
	name as Address Title.
	"""
	if address.landa_member:
		link_name = address.landa_member
		address.address_title = " ".join(
			frappe.get_value(
				"LANDA Member", address.landa_member, ["first_name", "last_name"]
			)
		)
	elif address.external_contact:
		link_name = address.external_contact
		address.address_title = " ".join(
			frappe.get_value(
				"External Contact", address.external_contact, ["first_name", "last_name"]
			)
		)
	elif address.organization:
		link_name = address.organization
		address.address_title = frappe.get_value("Organization", address.organization, "organization_name")

	if address.address_title and link_name:
		address.name = (
			f"{cstr(address.address_title).strip()} - {cstr(link_name).strip()}"
		)
		if frappe.db.exists("Address", address.name):
			address.name = make_autoname(f"{address.name}-.#")
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
			autoname(doc, None)	 # changes doc.name to the new name
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
				ignore_if_exists=True,	# don't rename if a record with the same name exists already
				show_alert=False,  # no need to show a UI alert, we're in the console
				rebuild_search=False,  # we do that explicitly at the end
			)
		except frappe.exceptions.ValidationError:
			continue

		frappe.db.commit()

	frappe.enqueue("frappe.utils.global_search.rebuild_for_doctype", doctype=doctype)
