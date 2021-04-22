# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "landa"
app_title = "LANDA"
app_publisher = "Landesverband Sächsischer Angler e. V.Real Experts GmbH"
app_description = "Datenmanagementsystem des "
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "office@realexperts.de"
app_license = "--"

fixtures = [
	"Organization",
	"Member Function Category",
	"Fishing Area",
	"Fish Species",
	"Item Attribute",
	{"dt": "Item", "filters": [["has_variants", "=", "1"]]},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/landa/css/landa.css"
# app_include_js = "/assets/landa/js/landa.js"

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
	"Delivery Note": "landa_sales/delivery_note/delivery_note.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
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
# after_install = "landa.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "landa.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Delivery Note": {
		"on_submit": "landa.landa_sales.delivery_note.delivery_note.on_submit",
		"validate": "landa.landa_sales.delivery_note.delivery_note.validate"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"landa.tasks.all"
# 	],
# 	"daily": [
# 		"landa.tasks.daily"
# 	],
# 	"hourly": [
# 		"landa.tasks.hourly"
# 	],
# 	"weekly": [
# 		"landa.tasks.weekly"
# 	]
# 	"monthly": [
# 		"landa.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "landa.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "landa.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "landa.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

