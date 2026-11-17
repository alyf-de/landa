import frappe
from frappe.utils import flt

from landa.water_body_management.doctype.stocking_site.stocking_site import (
	COORDINATE_PRECISION,
	get_location_point,
)


def execute():
	"""Set the new coordinate fields from the existing markers."""
	sites = frappe.get_all("Stocking Site", filters={"location": ("is", "set")}, fields=["name", "location"])
	for site in sites:
		point = get_location_point(site.location)
		if not point:
			continue

		frappe.db.set_value(
			"Stocking Site",
			site.name,
			{
				"longitude": flt(point[0], COORDINATE_PRECISION),
				"latitude": flt(point[1], COORDINATE_PRECISION),
			},
			update_modified=False,
		)
