import json

import frappe


def execute():
	"""
	Water Body: convert all MultiPolygons to Polygons in the geo shapes.

	Leaflet Draw doesn't support editing the MutiPolygons (imported from the
	former GIS), so we need to convert them to Polygons.
	"""
	for wb_name in frappe.get_all(
		"Water Body", filters={"location": ("like", "%MultiPolygon%")}, pluck="name"
	):
		geojson_str = frappe.db.get_value("Water Body", wb_name, "location")
		geojson = json.loads(geojson_str)

		if "features" not in geojson:
			continue

		features = []
		modified = False
		for feature in geojson["features"]:
			if feature["geometry"]["type"] != "MultiPolygon":
				features.append(feature)
			else:
				features.extend(
					{
						"type": "Feature",
						"geometry": {"type": "Polygon", "coordinates": polygon},
						"properties": feature["properties"],
					}
					for polygon in feature["geometry"]["coordinates"]
				)
				modified = True

		if modified:
			geojson["features"] = features
			frappe.db.set_value("Water Body", wb_name, "location", json.dumps(geojson))
