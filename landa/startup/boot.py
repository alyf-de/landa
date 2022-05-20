import frappe
from landa.utils import get_current_member_data


def boot_session(bootinfo):
	if frappe.session.user == "Guest":
		return

	bootinfo.landa = get_current_member_data()
