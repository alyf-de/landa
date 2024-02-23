// Copyright (c) 2021, Real Experts GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Water Body", {
	setup: function (frm) {
		frm.fields_dict.location.point_to_layer = pointToLayer;
		frm.fields_dict.location.on_each_feature = onEachFeature;
		frm.fields_dict.location.customize_draw_controls = customize_draw_controls;
	},

	refresh: function (frm) {
		if (
			!frm.is_new() &&
			frappe.boot.landa.regional_organization &&
			frm.doc.organization !== frappe.boot.landa.regional_organization
		) {
			frm.disable_form();
		}

		frm.trigger("bind_rotation");
		frm.trigger("update_draw");

		frm.set_query("icon", function (doc) {
			return {
				filters: {
					icon: ["is", "set"],
				},
			};
		});
	},
	location: function (frm) {
		frm.trigger("update_draw");
	},
	icon: function (frm) {
		frm.trigger("bind_rotation");
	},
	icon_path: function (frm) {
		frm.trigger("update_draw");
		frm.refresh_field("icon_preview");

		// reset rotation
		frm.rotation_angle = 0;
		get_rotation_element().value = 0;
		frm.trigger("bind_rotation");
	},
	draw_restricted_area: function (frm) {
		update_polygon_control(
			frm.fields_dict.location.draw_control,
			frm.doc.draw_restricted_area
		);
	},
	bind_rotation: function (frm) {
		if (!frm.doc.icon_path) {
			return;
		}

		bind_rotation_event(frm);
	},
	update_draw: function (frm) {
		update_draw_control(
			frm.fields_dict.location.draw_control,
			frm.doc.icon_path,
			frm.doc.icon,
			frm.rotation_angle,
		);
	},
});

function bind_rotation_event(frm) {
	const icon_rotation = get_rotation_element();
	const icon_preview = get_img_element(frm);
	icon_rotation.addEventListener("input", function (evt) {
		apply_rotation(icon_preview, evt.target.value);
		frm.rotation_angle = evt.target.value;
		frm.trigger("update_draw");
	});
}

function get_img_element(frm) {
	return frm.fields_dict.icon_preview.wrapper.getElementsByTagName("img")[0];
}

function get_rotation_element() {
	return document.getElementById("icon_rotation");
}

function apply_rotation(element, rotation_angle) {
	element.style.transform = `rotate(${rotation_angle}deg)`;
}

function update_draw_control(draw_control, icon_url, icon_name, rotation_angle) {
	if (!draw_control) {
		return;
	}
	let marker_config = {};

	if (icon_url) {
		const CustomIcon = L.Icon.extend({
			options: {
				iconSize: new L.Point(24, 24),
				iconUrl: icon_url,
				iconName: icon_name,
				rotationAngle: rotation_angle,
			},
		});
		marker_config.icon = new CustomIcon();
	}

	draw_control.setDrawingOptions({ marker: marker_config });
}


function update_polygon_control(draw_control, draw_restricted_area) {
	if (!draw_control) {
		return;
	}
	let polygon_config = {
		shapeOptions: {
			color: frappe.ui.color.get("blue"),
		},
	};

	if (draw_restricted_area) {
		polygon_config.shapeOptions.color = "red";
		polygon_config.shapeOptions.isRestrictedArea = true;
	}

	draw_control.setDrawingOptions({ polygon: polygon_config });
}


function pointToLayer(geoJsonPoint, latlng) {
	if (geoJsonPoint.properties.point_type == "circle"){
		return L.circle(latlng, {radius: geoJsonPoint.properties.radius});
	} else if (geoJsonPoint.properties.point_type == "circlemarker") {
		return L.circleMarker(latlng, {radius: geoJsonPoint.properties.radius});
	} else if (geoJsonPoint.properties.point_type == "custom-icon") {
		const marker = L.marker(
			latlng,
			{
				icon: L.icon({
					iconUrl: frappe.boot.icon_map[geoJsonPoint.properties.icon],
					iconSize: [24, 24],
				}),
				title: geoJsonPoint.properties.tooltip,
				alt: geoJsonPoint.properties.icon,
			}
		);
		marker.options.rotationAngle = geoJsonPoint.properties.rotation_angle;
		if (geoJsonPoint.properties.tooltip) {
			marker.bindTooltip(geoJsonPoint.properties.tooltip);
		}
		return marker;
	} else {
		const marker = L.marker(latlng);
		if (geoJsonPoint.properties.tooltip) {
			marker.bindTooltip(geoJsonPoint.properties.tooltip);
		}
		return marker;
	}
}

function onEachFeature(feature, layer) {
	if (feature.geometry.type == "Polygon" && feature.properties.is_restricted_area) {
		layer.setStyle({color: "red"});
	}
}

function customize_draw_controls() {
	const circleToGeoJSON = L.Circle.prototype.toGeoJSON;
	L.Circle.include({
		toGeoJSON: function() {
			const feature = circleToGeoJSON.call(this);
			feature.properties = {
				point_type: 'circle',
				radius: this.getRadius()
			};
			return feature;
		}
	});

	L.CircleMarker.include({
		toGeoJSON: function() {
			const feature = circleToGeoJSON.call(this);
			feature.properties = {
				point_type: 'circlemarker',
				radius: this.getRadius()
			};
			return feature;
		}
	});

	const markerToGeoJSON = L.Marker.prototype.toGeoJSON;
	const markerSetPosition = L.Marker.prototype._setPos;
	L.Marker.include({
		// Rotation inspired by https://github.com/bbecquet/Leaflet.RotatedMarker/blob/master/leaflet.rotatedMarker.js
		_setPos: function (pos) {
			markerSetPosition.call(this, pos);
			this._applyRotation();
		},

		_applyRotation: function () {
			if (this.options.rotationAngle) {
				this._icon.style[L.DomUtil.TRANSFORM+'Origin'] = 'center';

				const transformStyle = this._icon.style[L.DomUtil.TRANSFORM];
				if (!transformStyle.includes('rotate')) {
					this._icon.style[L.DomUtil.TRANSFORM] += ` rotate(${this.options.rotationAngle}deg)`;
				}
			}
		},

		toGeoJSON: function () {
			const feature = markerToGeoJSON.call(this);
			if (this.options.icon.options.iconName) {
				feature.properties = {
					point_type: 'custom-icon',
					icon: this.options.icon.options.iconName,
					rotation_angle: this.options.icon.options.rotationAngle,
				};
			}
			if (this._tooltip && this._tooltip._content) {
				feature.properties.tooltip = this._tooltip._content;
			}
			return feature;
		},
	});

	const polygonToGeoJSON = L.Polygon.prototype.toGeoJSON;
	L.Polygon.include({
		toGeoJSON: function() {
			const feature = polygonToGeoJSON.call(this);
			if (this.options.isRestrictedArea) {
				feature.properties = {
					is_restricted_area: true,
				};
			}
			return feature;
		}
	});

	L.Icon.Default.imagePath = '/assets/frappe/images/leaflet/';
}
