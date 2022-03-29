# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "landa"
app_title = "LANDA"
app_publisher = "Real Experts GmbH"
app_description = "Datenmanagementsystem des Landesverband Sächsischer Angler e. V."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "office@realexperts.de"
app_license = "--"

fixtures = [
	"System Settings",
	"Navbar Settings",
	"Website Settings",
	{
		"dt": "Web Page",
		"filters": [
			[
				"name",
				"in",
				[
					"über-landa",
					"impressum",
					"datenschutzangaben",
					"nutzungshinweise",
					"allgemeine-datenschutzinformation",
					"kurzzusammenfassung-zum-thema-datenschutz-für-mitglieder",
					"hilfe",
				],
			]
		],
	},
	"Contact Us Settings",
	"About Us Settings",
	"Module Profile",
	{"dt": "Role", "filters": [["name", "like", "%LANDA%"]]},
	{"dt": "Organization", "filters": [["name", "in", ["LV", "AVE", "AVS", "AVL"]]]},
	"Member Function Category",
	"Fish Species",
	"Fishing Area",
	{
		"dt": "Variant Field",
		"filters": [["field_name", "in", ["description", "item_tax_template"]]],
	},
	"Translation",
	{
		"doctype": "Letter Head",
		"filters": {"name": ["in", "Extended Information in Footer"]},
	},
	"Salutation",
	"Gender",
	{"dt": "Note", "filters": {"name": "Datenschutz Hinweise"}},
]


# DocTypes to be created once, after installation of this app
#
# Used for records that cannot be a fixture because they will be modified later.
# (Being fixtures would overwrite the data on every migrate.)
#
# ATTENTION: Below records cannot contain a "name" attribute as this will cause
# a validation error in frappe.
#
# Used in `landa.install.create_records_from_hooks`
landa_create_after_install = [
	{
		# Cannot be a fixture because it would overwrite Item Attribute Values
		# on every migrate
		"doctype": "Item Attribute",
		"attribute_name": "Erlaubnisscheinart",
	},
	{
		# Cannot be a fixture because it would accounts on every migrate
		"doctype": "Mode of Payment",
		"enabled": 1,
		"mode_of_payment": "Bar",
		"type": "Cash",
	},
	{
		# Cannot be a fixture because it would accounts on every migrate
		"doctype": "Mode of Payment",
		"enabled": 1,
		"mode_of_payment": "Bank\u00fcberweisung",
		"type": "Bank",
	},
	{
		"attribute_name": "G\u00fcltigkeitsjahr",
		"doctype": "Item Attribute",
		"from_range": 2021.0,
		"increment": 1.0,
		"numeric_values": 1,
		"to_range": 2030.0,
	},
	{
		"attribute_name": "Beitragsart",
		"doctype": "Item Attribute",
		"item_attribute_values": [
			{
				"abbr": "V",
				"attribute_value": "Vollzahler",
			},
			{
				"abbr": "F",
				"attribute_value": "F\u00f6rdermitglied",
			},
			{
				"abbr": "J",
				"attribute_value": "Jugend",
			},
			{
				"abbr": "A",
				"attribute_value": "Austauschmarke",
			},
		],
		"numeric_values": 0,
	},
	{
		"attribute_name": "Bundesland",
		"doctype": "Item Attribute",
		"item_attribute_values": [
			{
				"abbr": "SNA",
				"attribute_value": "Sachsen-Anhalt",
			},
			{
				"abbr": "BB",
				"attribute_value": "Brandenburg",
			},
			{
				"abbr": "TH",
				"attribute_value": "Th\u00fcringen",
			},
			{
				"abbr": "BE",
				"attribute_value": "Berlin",
			},
			{
				"abbr": "MV",
				"attribute_value": "Mecklenburg-Vorpommern",
			},
		],
		"numeric_values": 0,
	},
]

# Used in `landa.install.disable_modes_of_payment`
disable_modes_of_payment = [
	"Wire Transfer",
	"Cash",
	"Bank Draft",
	"Credit Card",
	"Cheque",
]

landa_add_to_session_defaults = ["Organization", "Customer"]

on_session_creation = "landa.overrides.set_user_defaults"

welcome_email = "landa.utils.welcome_email"

# treeviews = "Organization"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/landa/css/landa.css"
app_include_js = "/assets/landa/js/map_defaults.js"

# include js, css files in header of web template
# web_include_css = "/assets/landa/css/landa.css"
# web_include_js = "/assets/landa/js/landa.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "landa/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Delivery Note": "landa_stock/delivery_note/delivery_note.js",
	"Sales Order": "landa_sales/sales_order/sales_order.js",
	"Item": "landa_stock/item/item.js",
	"Payment Entry": "landa_sales/payment_entry/payment_entry.js",
}
doctype_list_js = {"Report" : "scripts/report_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "landa.install.before_install"
after_install = "landa.install.after_install"
after_migrate = "landa.migrate.after_migrate"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "landa.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Report": "landa.permissions.report_query",
}

# has_permission = {
#	"Contact": "landa.address_and_contact.has_permission",
#	"Address": "landa.address_and_contact.has_permission"
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Delivery Note": {
		"on_submit": "landa.landa_stock.delivery_note.delivery_note.on_submit",
		"before_validate": "landa.landa_stock.delivery_note.delivery_note.before_validate",
		"validate": "landa.landa_stock.delivery_note.delivery_note.validate",
		"autoname": "landa.landa_stock.delivery_note.delivery_note.autoname",
	},
	"Item": {
		"before_insert": "landa.landa_stock.item.item.before_insert",
		"autoname": "landa.landa_stock.item.item.autoname",
	},
	"Item Price": {"validate": "landa.landa_sales.item_price.item_price.validate"},
	"Sales Order": {
		"before_validate": "landa.landa_sales.sales_order.sales_order.before_validate",
		"autoname": "landa.landa_sales.sales_order.sales_order.autoname",
	},
	"Sales Invoice": {
		"before_validate": "landa.landa_sales.sales_invoice.sales_invoice.before_validate",
		"autoname": "landa.landa_sales.sales_invoice.sales_invoice.autoname",
	},
	"Payment Entry": {
		"before_validate": "landa.landa_sales.payment_entry.pament_entry.before_validate",
		"autoname": "landa.landa_sales.payment_entry.pament_entry.autoname",
	},
	"Address": {
		"validate": "landa.address_and_contact.validate",
		"autoname": "landa.organization_management.address.address.autoname",
	},
	"Contact": {
		"validate": "landa.address_and_contact.validate",
		"after_insert": "landa.organization_management.contact.contact.after_insert",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	#	"all": [
	#		"landa.tasks.all"
	#	],
	"daily": ["landa.tasks.daily"],
	# "all": ["landa.tasks.all"],
	#	, "hourly": [
	#		"landa.tasks.hourly"
	#	],
	#	"weekly": [
	#		"landa.tasks.weekly"
	#	]
	#	"monthly": [
	#		"landa.tasks.monthly"
	#	]
}

# Testing
# -------

# before_tests = "landa.install.before_tests"

# Overriding Methods
# ------------------------------
#

override_whitelisted_methods = {
	# Use frappe's send message so that the website contact form doesn't create a Lead and Opportunity
	"erpnext.templates.utils.send_message": "frappe.www.contact.send_message"
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "landa.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]
# jenv = {
#	"methods": [
#		"debug_print_var:landa.landa_sales.sales_order.sales_order.debug_print_var"
#	]
# }
