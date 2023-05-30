### Create Demo Accounts

This app provide a bench command `make-demo-accounts`. This is useful for testing permissions. You can use it to create a **Member**, **Member Function** and **User** for every existing **Member Function Category**, in an existing local organization.

Prerequisites:

1. Create a [Local Organization](organizations-and-members.md)
2. Define some [Member Function Categories](permissions.md)

Now you can run the following command (replace `$SITE` and `$ORGANIZATION` with your specific values):

```bash
bench --site $SITE make-demo-accounts $ORGANIZATION
```

### Import water bodies from GeoJSON

This app provide a bench command `import-geojson`. This is useful for importing water body shapes from a GeoJSON file.

```bash
bench --site $SITE import-geojson /path/to/file.geojson
```

The GeoJSON file is expected to look approximately like this:

```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": { "GEW_ID": "D07-158" },
            "geometry": {"..."},
        },
        "..."
    ]
}
```

All features must have a `GEW_ID` property. The value of this property will be used for finding the water body.

All current GeoJSON information of a Water Body will be replaced with the new information from the file.
