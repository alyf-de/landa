# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet
from frappe.desk.treeview import make_tree_args

class Organization(NestedSet):
	nsm_parent_field = 'parent_organization'


@frappe.whitelist()
def get_children(doctype, parent=None, organization=None, is_root=False):
	if parent == None or parent == "All Organizations":
		parent = ""

	return frappe.get_list(doctype, fields=[
			'name as value',
			'organization_name as title',
			'is_group as expandable'
		],
		filters={
			'parent_organization': parent
		}
	)


@frappe.whitelist()
def add_node():
	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_company == 'All Organizations':
		args.parent_company = None

	frappe.get_doc(args).insert()
