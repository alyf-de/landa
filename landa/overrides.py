# -*- coding: utf-8 -*-
# Copyright (c) 2021, Landesverband Sächsischer Angler e. V.Real Experts GmbH and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import frappe


def set_user_defaults():
    frappe.defaults.set_user_default(
        "organization",
        frappe.get_value("Member", {"user": frappe.session.user}, "organization"),
    )
