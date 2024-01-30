The `location` field in **Water Body** contains a GeoJSON object.

This is available via the API endpoint [`/api/method/landa.api.water_body`](api.md#water-body). In the API response, the property is called `geojson`.

The GeoJSON object contains a `FeatureCollection`, for example:

```js
{
    "type": "FeatureCollection",
    "features": [
        { // water body area
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [14.326696, 51.174984],
                        [14.326345, 51.17503],
                        [14.324878, 51.175383],
                        [14.323545, 51.175964],
                        [14.323442, 51.17628],
                        [14.323064, 51.17645],
                        [14.323376, 51.177352],
                        [14.324741, 51.176883],
                        [14.326346, 51.176331],
                        [14.327334, 51.176162],
                        [14.327485, 51.176114],
                        [14.327215, 51.175865],
                        [14.327004, 51.175578],
                        [14.326856, 51.17531],
                        [14.326696, 51.174984]
                    ]
                ]
            },
        },
        { // restricted area
            "type": "Feature",
            "properties": { "is_restricted_area": true },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [14.323533, 51.177293],
                        [14.323232, 51.177468],
                        [14.322867, 51.176466],
                        [14.323136, 51.176418],
                        [14.323329, 51.176324],
                        [14.323457, 51.17621],
                        [14.323597, 51.17623],
                        [14.323479, 51.176405],
                        [14.323221, 51.176492],
                        [14.323533, 51.177293]
                    ]
                ]
            }
        },
        { // default marker
            "type": "Feature",
            "properties": {},
            "geometry": { "type": "Point", "coordinates": [14.322559, 51.175095] }
        },
        { // default marker with tooltip
            "type": "Feature",
            "properties": { "tooltip": "Yay!" },
            "geometry": { "type": "Point", "coordinates": [14.324146, 51.174597] }
        },
        { // marker with custom icon
            "type": "Feature",
            "properties": {
                "point_type": "custom-icon",
                "icon": "hs-gelb-f-gelb",
                "rotation_angle": 0
            },
            "geometry": { "type": "Point", "coordinates": [14.324627, 51.174543] }
        },
        { // marker with custom icon and tooltip
            "type": "Feature",
            "properties": {
                "point_type": "custom-icon",
                "icon": "hs-gelb-f-rot",
                "rotation_angle": 0,
                "tooltip": "Yay!"
            },
            "geometry": { "type": "Point", "coordinates": [14.326644, 51.174287] }
        }
    ]
}
```

The icon URL for a given icon name can be obtained via the API endpoint [`/api/method/landa.api.custom_icon`](api.md#custom-icon).
