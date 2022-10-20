import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.nestedset import get_ancestors_of


def get_new_name(prefix, company, doctype):
	"""
	Create a document name like prefix-company-year-####.

	For example 'ZAHL-AVS-2021-0001'.
	"""
	from frappe.model.naming import make_autoname
	from frappe.utils.data import nowdate

	company_abbr = frappe.get_value("Company", company, "abbr")
	current_year = nowdate()[:4]  # note: y10k problem
	return make_autoname(f"{prefix}-{company_abbr}-{current_year}-.####", doctype)


def welcome_email():
	lang = frappe.db.get_single_value("System Settings", "language")
	site_name = "LANDA"
	title = _("Welcome to {0}", lang=lang).format(site_name)
	return title


def reset_workspace(workspace: str) -> None:
	"""Delete all user's custom extensions of `workspace`.

	Used to reset user customizations after the workspace definition has changed."""
	custom_workspaces = frappe.get_all(
		"Workspace",
		filters={"for_user": ("is", "set"), "extends": workspace},
		pluck="name",
	)
	for workspace_name in custom_workspaces:
		frappe.delete_doc("Workspace", workspace_name)


def get_current_member_data():
	from_cache = frappe.cache().hget("landa", frappe.session.user)
	if from_cache:
		return from_cache

	result = frappe._dict()
	data = frappe.db.get_value(
		"LANDA Member",
		filters={"user": frappe.session.user},
		fieldname=["name", "organization"],
	)

	if not data:
		frappe.cache().hset("landa", frappe.session.user, result)
		return result

	member_name, member_organization = data
	member_organization = member_organization[
		:7
	]  # use local Organization instead of Ortsgruppe

	ancestors = get_ancestors_of("Organization", member_organization)
	ancestors.reverse()  # root as the first element

	result.member = member_name
	result.local_organization = member_organization
	result.regional_organization = ancestors[1]
	result.state_organization = ancestors[0]

	frappe.cache().hset("landa", frappe.session.user, result)

	return result


def db_unset(doctype: str, field: str, value: str) -> None:
	"""In all records of `doctype` where `field` is equal to `value`, set field to `None`."""
	table = frappe.qb.DocType(doctype)
	frappe.qb.update(table).set(table[field], None).where(table[field] == value).run()


def db_delete(doctype: str, field: str, value: str) -> None:
	"""Delete all records of `doctype` where `field` is equal to `value`."""
	table = frappe.qb.DocType(doctype)
	frappe.qb.from_(table).delete().where(table[field] == value).run()


def remove_from_table(table_doctype: str, link_field: str, value: str):
	table = frappe.qb.DocType(table_doctype)
	query = frappe.qb.from_(table).select(
		table.parenttype, table.parent, table.parentfield, table.idx
	).where(table[link_field] == value).distinct()

	for parent_type, parent_name, parent_field, idx in query.run():
		doc = frappe.get_doc(parent_type, parent_name)
		doc.get(parent_field).pop(idx - 1)
		doc.save(ignore_permissions=True)


def delete_dynamically_linked(doctype: str, linked_doctype: str, linked_name: str):
	dl = frappe.qb.DocType("Dynamic Link")
	for result in (
		frappe.qb.from_(dl).select(dl.parent).where(
			(dl.parenttype == doctype) & (dl.link_doctype == linked_doctype) & (dl.link_name == linked_name)
		).run()
	):
		doc: Document = frappe.get_doc(doctype, result[0])
		if len(doc.links) == 1:
			frappe.delete_doc(
				doctype, doc.name, delete_permanently=True, ignore_permissions=True
			)


def get_link_fields(doctype: str, as_dict: int = 1):
	# TODO: handle fields changed by Property Setter(?)
	return frappe.db.sql(
		"""
		SELECT
			parent,
			fieldname,
			reqd,
			(SELECT issingle FROM tabDocType dt WHERE dt.name = df.parent) AS issingle,
			(SELECT istable FROM tabDocType dt WHERE dt.name = df.parent) AS istable
		FROM tabDocField df
		WHERE
			df.options=%(doctype)s AND df.fieldtype='Link'

		UNION DISTINCT

		SELECT
			dt AS parent,
			fieldname,
			reqd,
			(SELECT issingle FROM tabDocType dt WHERE dt.name = df.dt) AS issingle,
			(SELECT istable FROM tabDocType dt WHERE dt.name = df.dt) AS istable
		FROM `tabCustom Field` df
		WHERE
			df.options=%(doctype)s AND df.fieldtype='Link'
		""", {"doctype": doctype}, as_dict=as_dict)


def purge_all(doctype: str, name: str) -> None:
	for link_field in get_link_fields(doctype):
		if link_field["istable"]:
			remove_from_table(link_field["parent"], link_field["fieldname"], name)
		elif link_field["reqd"] == 0:
			db_unset(link_field["parent"], link_field["fieldname"], name)
		elif not link_field["issingle"]:
			db_delete(link_field["parent"], link_field["fieldname"], name)
		else:  # mandatory link to doctype in single doctype.
			continue
