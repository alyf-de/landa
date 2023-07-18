import frappe

from landa.utils import get_current_member_data
from landa.water_body_management.doctype.custom_icon.custom_icon import get_icon_map


def boot_session(bootinfo):
	if frappe.session.user == "Guest":
		return

	bootinfo.landa = get_current_member_data()
	bootinfo.icon_map = get_icon_map()
