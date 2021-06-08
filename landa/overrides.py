# -*- coding: utf-8 -*-
# Copyright (c) 2021, Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import os

import frappe
from frappe.translate import get_translation_dict_from_file


def set_user_defaults():
    organization = frappe.get_value("Member", {"user": frappe.session.user}, "organization")
    if not organization:
        return

    frappe.defaults.set_user_default("organization", organization)
    frappe.defaults.set_user_default("company", get_default_company(organization))
    frappe.defaults.set_user_default("customer", organization)


def get_default_company(organization):
    doc = frappe.get_doc("Organization", organization)
    ancestors = doc.get_ancestors()

    if len(ancestors) < 2:
        return None

    ancestors.reverse()
    regional_organization = ancestors[1]

    return frappe.get_value("Company", {"abbr": regional_organization})


def get_translated_dict():
    """Return a dict with this app's translations for the current user's language."""
    app = "landa"
    lang = frappe.local.lang
    path = os.path.join(frappe.get_pymodule_path(app), "translations", lang + ".csv")

    return get_translation_dict_from_file(path, lang, app)
