// Copyright (c) 2026, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stocking Site", {
	setup(frm) {
		const field = frm.fields_dict.location;
		field.get_leaflet_controls = () => get_marker_controls(field);
		field.bind_leaflet_event_listeners = () => bind_map_events(field);
	},

	refresh(frm) {
		frm.trigger("show_water_body");
	},

	water_body(frm) {
		frm.trigger("show_water_body");
	},

	location(frm) {
		frm.trigger("show_water_body");
	},

	show_water_body(frm) {
		const field = frm.fields_dict.location;
		if (!field.map) {
			return;
		}

		remove_water_body_layer(field);
		if (!frm.doc.water_body) {
			return;
		}

		const water_body = frm.doc.water_body;
		frappe
			.xcall(
				"landa.water_body_management.doctype.stocking_site.stocking_site.get_water_body_map_data",
				{ water_body },
			)
			.then(({ location, margin_meters }) => {
				if (frm.doc.water_body !== water_body || !location) {
					return;
				}

				field.water_body_margin_meters = margin_meters;
				field.water_body_geojson = JSON.parse(location);
				field.water_body_layer = window.L.geoJSON(field.water_body_geojson, {
					filter: ({ geometry }) => ["Polygon", "MultiPolygon"].includes(geometry.type),
					style: ({ properties }) => ({
						color: properties.is_restricted_area ? "red" : frappe.ui.color.get("blue"),
						fillOpacity: 0.08,
					}),
				}).addTo(field.map);

				const bounds = field.water_body_layer.getBounds();
				if (!bounds.isValid()) {
					return;
				}

				const max_bounds = window.L.latLngBounds(
					bounds.getSouthWest().toBounds(margin_meters * 2),
				).extend(bounds.getNorthEast().toBounds(margin_meters * 2));
				field.map.invalidateSize();
				field.map.setMaxBounds(max_bounds);
				field.map.options.maxBoundsViscosity = 1;
				field.map.setMinZoom(
					Math.min(field.map.getBoundsZoom(max_bounds), field.map.getMaxZoom()),
				);
				field.map.fitBounds(bounds, { padding: [30, 30] });
			});
	},

	validate(frm) {
		get_location_point(frm.doc.location);
	},
});

function get_marker_controls(field) {
	return new window.L.Control.Draw({
		position: "topleft",
		draw: {
			polyline: false,
			polygon: false,
			rectangle: false,
			circle: false,
			circlemarker: false,
			marker: { repeatMode: false },
		},
		edit: {
			featureGroup: field.editableLayers,
			edit: false,
			remove: true,
		},
	});
}

function bind_map_events(field) {
	field.map.on("draw:created", async ({ layer, layerType }) => {
		if (layerType !== "marker") {
			return;
		}
		if (field.editableLayers.getLayers().length) {
			frappe.msgprint(__("Only one location marker is allowed."));
			return;
		}

		const water_body = field.frm.doc.water_body;
		if (!water_body) {
			frappe.msgprint(__("Select a Water Body before placing a marker."));
			return;
		}

		const latlng = layer.getLatLng();
		const is_valid = await frappe.xcall(
			"landa.water_body_management.doctype.stocking_site.stocking_site.is_point_near_water_body",
			{
				water_body,
				longitude: latlng.lng,
				latitude: latlng.lat,
			},
		);
		if (field.frm.doc.water_body !== water_body) {
			return;
		}
		if (!is_valid) {
			frappe.msgprint(
				__("The location marker must be within {0} m of the Water Body.", [
					field.water_body_margin_meters,
				]),
			);
			return;
		}
		if (field.editableLayers.getLayers().length) {
			frappe.msgprint(__("Only one location marker is allowed."));
			return;
		}

		field.editableLayers.addLayer(layer);
		set_location_value(field);
	});

	field.map.on("draw:deleted", () => set_location_value(field));
}

function set_location_value(field) {
	field.set_value(JSON.stringify(field.editableLayers.toGeoJSON()));
}

function remove_water_body_layer(field) {
	if (field.water_body_layer) {
		field.map.removeLayer(field.water_body_layer);
		delete field.water_body_layer;
	}
	delete field.water_body_geojson;
	delete field.water_body_margin_meters;
	field.map.setMaxBounds(null);
	field.map.setMinZoom(0);
}

function get_location_point(location) {
	if (!location) {
		return null;
	}

	const geojson = JSON.parse(location);
	if (geojson.type === "FeatureCollection" && geojson.features.length === 0) {
		return null;
	}
	if (
		geojson.type !== "FeatureCollection" ||
		geojson.features.length !== 1 ||
		geojson.features[0].geometry.type !== "Point"
	) {
		frappe.throw(__("At most one location marker is allowed."));
	}
	return geojson.features[0].geometry.coordinates;
}
