# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def set_user_defaults():
    organization = frappe.get_value("LANDA Member", {"user": frappe.session.user}, "organization")
    if not organization:
        return

    if not organization.endswith("000"):
        # Default organization should not be set for members of a regional organization (ending with 000)
        frappe.defaults.set_user_default("organization", organization)

    frappe.defaults.set_user_default("company", get_default_company(organization))
    # Customer is always the local organization (first seven digits of the organization)
    frappe.defaults.set_user_default("customer", organization[:7])


def get_default_company(organization):
    doc = frappe.get_doc("Organization", organization)
    ancestors = doc.get_ancestors()

    if len(ancestors) < 2:
        return None

    ancestors.reverse()
    regional_organization = ancestors[1]

    return frappe.get_value("Company", {"abbr": regional_organization})
