from . import __version__ as app_version

app_name = "rental"
app_title = "Rental"
app_publisher = "Viral Patel"
app_description = "Rental"
app_email = "viral@fosserp.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/rental/css/rental.css"
# app_include_js = "/assets/rental/js/rental.js"

# include js, css files in header of web template
# web_include_css = "/assets/rental/css/rental.css"
# web_include_js = "/assets/rental/js/rental.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "rental/public/scss/website"

# include js, css files in header of web form
webform_include_js = {"Room Booking": "public/js/room_booking.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}
app_include_js = [
	"rental.bundle.js"
]
# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Customer" : "public/js/customer.js"}
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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "rental.utils.jinja_methods",
#	"filters": "rental.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "rental.install.before_install"
# after_install = "rental.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "rental.uninstall.before_uninstall"
# after_uninstall = "rental.uninstall.after_uninstall"
scheduler_events = {
	"cron": {
		"0/1 * * * *": [
			"rental.rental.doctype.room_booking.room_booking.convert_inactive_booking",
			"rental.rental.doctype.equipment_booking.equipment_booking.convert_inactive_booking"
		],
    },
	"daily": [
		"rental.api.check_subscription_period"
	],
}
# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rental.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
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
	"Customer": {
		"validate": "rental.api.create_warehouse",
	},
	"Equipment":{
		"validate":[
			"rental.api.create_item_from_equipment",
		]
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"rental.tasks.all"
#	],
#	"daily": [
#		"rental.tasks.daily"
#	],
#	"hourly": [
#		"rental.tasks.hourly"
#	],
#	"weekly": [
#		"rental.tasks.weekly"
#	],
#	"monthly": [
#		"rental.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "rental.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "rental.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "rental.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["rental.utils.before_request"]
# after_request = ["rental.utils.after_request"]

# Job Events
# ----------
# before_job = ["rental.utils.before_job"]
# after_job = ["rental.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"rental.auth.validate"
# ]
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from rental.api import set_actual_qty
StockEntry.set_actual_qty = set_actual_qty