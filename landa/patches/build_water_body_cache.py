import frappe

from landa.water_body_management.doctype.water_body.water_body import build_water_body_cache


def execute():
	build_water_body_cache()  # Cache all Water Bodies

	fishing_areas = frappe.get_all("Fishing Area", pluck="name")
	for area in fishing_areas:
		build_water_body_cache(fishing_area=area)  # Cache Fishing Area wise
