import requests
import frappe
from thefuzz import fuzz
from thefuzz import process
from html import unescape
import json


def execute():
	organizations = get_organizations()
	organization_ids_by_name = {
		org["organization_name"]: org["name"] for org in organizations
	}
	data = get_data()

	for record in data:
		org_name = record.get("verein")
		if not org_name:
			continue

		org_name = unescape(org_name)
		result, score = process.extractOne(
			org_name,
			organization_ids_by_name.keys(),
			processor=clean_org_name,
			scorer=fuzz.token_set_ratio,
		)
		if score < 75:
			continue

		org_id = organization_ids_by_name[result]

		website = record.get("webseite")
		leaflet = record.get("leaflet", dict())
		lat = leaflet.get("lat")
		lng = leaflet.get("lng")

		doc = frappe.get_doc("Organization", org_id)
		if website and not doc.website:
			doc.website = website

		doc.location = get_geojson(lat, lng)
		doc.save()


def get_organizations():
	return frappe.get_all(
		"Organization",
		filters={"name": ("like", "AVE-%")},
		fields=["name", "organization_name"],
	)


def get_data():
	url = "https://www.anglerverband-sachsen.de/wp-json/api/v1/vereine"
	resp = requests.get(url)
	resp.raise_for_status()
	return resp.json()


def clean_org_name(org_name):
	for s in [
		"AV",
		"e. V.",
		"Verein",
		"Anglerverein",
		"Angelverein",
		"Angelfreunde",
		"Angelclub",
		"Angelsportverein",
		"ASV",
		"Anglererein",
		"Anglervereinigung",
		"Dresden",
		"Angleverein",
		"Deutscher Anglerverein",
		"Fischereiverein",
		"Sportfischerverein",
	]:
		if s in org_name:
			org_name = org_name.replace(s, "")

	return org_name.strip()


def get_geojson(lat, lng):
	return json.dumps(
		{
			"type": "FeatureCollection",
			"features": [
				{
					"type": "Feature",
					"properties": {},
					"geometry": {"type": "Point", "coordinates": [lng, lat]},
				}
			],
		},
		separators=(',', ':')
	)
