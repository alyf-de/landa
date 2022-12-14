import frappe
from frappe import get_hooks
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def after_install():
	update_system_settings()
	make_custom_fields()
	make_property_setters()
	create_records_from_hooks()
	disable_modes_of_payment()
	add_session_defaults()
	setup_uoms()
	update_stock_settings()


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
	ref_doctypes = get_hooks(
		"landa_add_to_session_defaults", default=[], app_name="landa"
	)
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
	frappe.qb.update(uom_table).set(uom_table.enabled, 0).where(
		uom_table.uom_name != "Anzahl"
	).run()


def update_system_settings():
	settings = frappe.get_single("System Settings")
	settings.update(
		{
			"allow_error_traceback": 0,
			"allow_guests_to_upload_files": 0,
			"apply_strict_user_permissions": 1,
			"attach_view_link": 1,
			"country": "Germany",
			"date_format": "dd.mm.yyyy",
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
	create_custom_fields(frappe.get_hooks("landa_custom_fields"))


def make_property_setters():
	for doctypes, property_setters in frappe.get_hooks(
		"landa_property_setters", {}
	).items():
		if isinstance(doctypes, str):
			doctypes = (doctypes,)

		for doctype in doctypes:
			for property_setter in property_setters:
				for_doctype = True if not property_setter[0] else False
				make_property_setter(doctype, *property_setter, for_doctype)


def update_stock_settings():
	frappe.db.set_value(
		"Stock Settings",
		None,
		"role_allowed_to_over_deliver_receive",
		"LANDA Member",
		update_modified=False,
	)
