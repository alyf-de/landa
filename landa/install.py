import os

import frappe
from frappe import get_hooks
from frappe.core.doctype.doctype.doctype import validate_fields_for_doctype
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.customize_form.customize_form import (
	docfield_properties,
	doctype_properties,
)
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

import landa

from .custom_fields import get_custom_fields
from .doc_perms import get_doc_perms
from .property_setters import get_property_setters


def after_install():
	complete_setup_wizard_for_test()
	update_system_settings()
	sync_customizations()
	create_records_from_hooks()
	disable_modes_of_payment()
	add_session_defaults()
	setup_uoms()
	update_stock_settings()
	update_accounts_settings()


def sync_customizations():
	make_custom_fields()
	make_property_setters()
	make_doc_perms()


def create_records_from_hooks():
	records = get_hooks("landa_create_after_install", default=[], app_name="landa")
	for record in records:
		try:
			doc = frappe.get_doc(record)
			doc.save()
		except frappe.DuplicateEntryError:
			continue


def disable_modes_of_payment():
	names = get_hooks("disable_modes_of_payment", default=[], app_name="landa")
	for name in names:
		try:
			frappe.set_value("Mode of Payment", name, "enabled", False)
		except frappe.DoesNotExistError:
			continue


def add_session_defaults():
	ref_doctypes = get_hooks("landa_add_to_session_defaults", default=[], app_name="landa")
	settings = frappe.get_single("Session Default Settings")
	settings.extend(
		"session_defaults",
		[
			{"ref_doctype": ref_doctype}
			for ref_doctype in set(ref_doctypes).difference(
				{row.ref_doctype for row in settings.session_defaults}
			)
		],
	)

	settings.save()


def setup_uoms():
	# create new UOM "Anzahl"
	if not frappe.db.exists("UOM", "Anzahl"):
		doc = frappe.new_doc("UOM")
		doc.uom_name = "Anzahl"
		doc.insert()

	# Disable all other UOMs
	uom_table = frappe.qb.DocType("UOM")
	frappe.qb.update(uom_table).set(uom_table.enabled, 0).where(uom_table.uom_name != "Anzahl").run()


def update_system_settings():
	settings = frappe.get_single("System Settings")
	settings.update(
		{
			"allow_error_traceback": 0,
			"allow_guests_to_upload_files": 0,
			"apply_strict_user_permissions": 1,
			"apply_perm_level_on_api_calls": 1,
			"allow_older_web_view_links": 0,
			"attach_view_link": 1,
			"country": "Germany",
			"date_format": "dd.mm.yyyy",
			"disable_document_sharing": 1,
			"disable_change_log_notification": 1,
			"disable_system_update_notification": 1,
			"email_footer_address": "Bitte antworten Sie nicht auf diese automatische E-Mail. Die Antworten werden nicht gelesen. Bei Fragen wenden Sie sich bitte an Ihren Regionalverband.",
			"enable_onboarding": 0,
			"enable_password_policy": 1,
			"first_day_of_the_week": "Monday",
			"float_precision": "3",
			"language": "de",
			"minimum_password_score": "3",
			"number_format": "#.###,##",
			"time_format": "HH:mm",
			"time_zone": "Europe/Berlin",
		}
	)
	settings.save()


def make_custom_fields():
	create_custom_fields(get_custom_fields())


def make_doc_perms():
	"""Seed Custom DocPerm rows on fresh installs only.

	Existing sites are left untouched: if any Custom DocPerm already exists for a
	parent doctype, we assume that's the authoritative state. The legacy fixture
	JSONs used to wipe and re-insert on every migrate; we deliberately don't
	reproduce that to avoid clobbering UI-driven changes.
	"""
	for doctype, perms in get_doc_perms().items():
		if frappe.db.exists("Custom DocPerm", {"parent": doctype}):
			continue

		for perm in perms:
			frappe.get_doc(
				{
					"doctype": "Custom DocPerm",
					"parent": doctype,
					"parenttype": "DocType",
					"parentfield": "permissions",
					**perm,
				}
			).db_insert()


def make_property_setters():
	for doctypes, property_setters in get_property_setters().items():
		if isinstance(doctypes, str):
			doctypes = (doctypes,)

		for doctype in doctypes:
			for property_setter in property_setters:
				if property_setter[0]:
					for_doctype = False
					property_type = docfield_properties.get(
						property_setter[1],
					)
				else:
					for_doctype = True
					property_type = doctype_properties.get(
						property_setter[1], "Data"
					)  # Data fallback for field_order

				make_property_setter(
					doctype=doctype,
					fieldname=property_setter[0],
					property=property_setter[1],
					value=property_setter[2],
					property_type=property_type,
					for_doctype=for_doctype,
					validate_fields_for_doctype=False,
				)

			validate_fields_for_doctype(doctype)


def update_stock_settings():
	frappe.db.set_single_value(
		"Stock Settings",
		"role_allowed_to_over_deliver_receive",
		"LANDA Member",
		update_modified=False,
	)


def update_accounts_settings():
	frappe.db.set_single_value(
		"Accounts Settings",
		"role_allowed_to_over_bill",
		"LANDA Member",
		update_modified=False,
	)


def complete_setup_wizard_for_test():
	"""
	Complete setup wizard where UI intervention is not carried out (CI, Running tests, etc).
	"""
	site = frappe.local.site
	allow_tests = frappe.get_conf(site).allow_tests
	if allow_tests or os.environ.get("CI"):
		landa.complete_setup_wizard_for_test()
