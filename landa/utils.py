from typing import Optional
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.dynamic_links import get_dynamic_link_map
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


def remove_from_table(table_doctype: str, link_field: str, value: str):
	table = frappe.qb.DocType(table_doctype)
	query = (
		frappe.qb.from_(table)
		.select(table.parenttype, table.parent, table.parentfield, table.idx)
		.where(table[link_field] == value)
		.distinct()
	)

	for parent_type, parent_name, parent_field, idx in query.run():
		pop_from_table(parent_type, parent_name, parent_field, idx)


def pop_from_table(parent_type, parent_name, parent_field, idx):
	doc = frappe.get_doc(parent_type, parent_name)
	doc.get(parent_field).pop(idx - 1)
	doc.save(ignore_permissions=True)


def delete_dynamically_linked(
	doctype: str, linked_doctype: str, linked_name: str
) -> None:
	"""Delete all records of `doctype` that are linked to `linked_name` of `linked_doctype` via a Dynamic Link table."""
	dl = frappe.qb.DocType("Dynamic Link")
	for name, parent_field, idx in (
		frappe.qb.from_(dl)
		.select(dl.parent, dl.parentfield, dl.idx)
		.where(
			(dl.parenttype == doctype)
			& (dl.link_doctype == linked_doctype)
			& (dl.link_name == linked_name)
		)
		.run()
	):
		doc: Document = frappe.get_doc(doctype, name)
		if any(
			row
			for row in doc.links
			if row.link_doctype == linked_doctype and row.link_name != linked_name
		):
			# if there are links to records of the same doctype, for example, an
			# address belonging to multiple members
			pop_from_table(doctype, name, parent_field, idx)

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
			(SELECT issingle FROM tabDocType dt WHERE dt.name = df.parent) AS is_in_single,
			(SELECT istable FROM tabDocType dt WHERE dt.name = df.parent) AS is_in_table
		FROM tabDocField df
		WHERE
			df.options=%(doctype)s AND df.fieldtype='Link'

		UNION DISTINCT

		SELECT
			dt AS parent,
			fieldname,
			reqd,
			(SELECT issingle FROM tabDocType dt WHERE dt.name = df.dt) AS is_in_single,
			(SELECT istable FROM tabDocType dt WHERE dt.name = df.dt) AS is_in_table
		FROM `tabCustom Field` df
		WHERE
			df.options=%(doctype)s AND df.fieldtype='Link'
		""",
		{"doctype": doctype},
		as_dict=as_dict,
	)


def purge_all(doctype: str, name: str) -> None:
	delete_linked_records(doctype, name)
	delete_dynamically_linked_records(doctype, name)


def delete_linked_records(doctype: str, name: str) -> None:
	for link_field in get_link_fields(doctype):
		d_doctype = link_field["parent"]
		d_link_field = link_field["fieldname"]
		if link_field["is_in_table"]:
			remove_from_table(d_doctype, d_link_field, name)
			continue

		if link_field["is_in_single"]:
			if not link_field["reqd"] and frappe.db.get_single_value(d_doctype, d_link_field) == name:
				unset_value(d_doctype, None, d_link_field, None)
			continue

		to_delete = frappe.get_all(
			d_doctype,
			filters={d_link_field: name},
			pluck="name",
		)
		for d_name in to_delete:
			if link_field["reqd"]:
				frappe.delete_doc(
					d_doctype,
					d_name,
					ignore_permissions=True,
					ignore_missing=True,
					delete_permanently=True,
				)
			else:
				unset_value(d_doctype, d_name, d_link_field)


def delete_dynamically_linked_records(doctype: str, name: str) -> None:
	for dynamic_link in get_dynamic_link_map().get(doctype, []):
		# delete all records that are linked to this record via a dynamic link field
		d_doctype = dynamic_link["parent"]
		d_link_field = dynamic_link["fieldname"]

		link_is_mandatory = frappe.get_meta(d_doctype).get_field(d_link_field).reqd
		for d_docname in frappe.get_all(
			d_doctype,
			filters={
				d_link_field: name,
				dynamic_link["options"]: doctype,
			},
			pluck="name",
		):
			if link_is_mandatory:
				frappe.delete_doc(
					d_doctype,
					d_docname,
					ignore_permissions=True,
					ignore_missing=True,
					delete_permanently=True,
				)
			else:
				unset_value(d_doctype, d_docname, d_link_field)


def unset_value(doctype: str, name: Optional[str], fieldname: str) -> None:
	doc = frappe.get_doc(doctype, name)
	if doc.meta.is_submittable and doc.docstatus > 0:
		doc.db_set(fieldname, None)
	else:
		doc.set(fieldname, None)
		doc.save(ignore_permissions=True, ignore_version=True)
