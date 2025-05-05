import frappe

from landa.utils import get_current_member_data
from landa.water_body_management.doctype.custom_icon.custom_icon import get_icon_map


def boot_session(bootinfo):
	if frappe.session.user == "Guest":
		return

	bootinfo.landa = get_current_member_data()
	bootinfo.icon_map = get_icon_map()
	bootinfo.company_abbr_map = get_company_abbr_map()


def get_company_abbr_map():
	"""Return a map of company name to company abbreviation."""
	return {d.name: d.abbr for d in frappe.get_list("Company", fields=["name", "abbr"])}
