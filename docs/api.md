## Organization

Get a list of organizations organizations with ID, organization name, geojson, address and contact.

- `GET /api/method/landa.api.organization`

    Parameters:

    - `id` (optional): return only data of the organization with this ID.

### Example Requests

> Remember to set the environment variable `BASE_URL` to the URL of your LANDA instance. For example like this: `export BASE_URL=https://lvsa-landa.de`

Get all Organizations:

```bash
curl --location "$BASE_URL/api/method/landa.api.organization"
```

Get a specific organization:

```bash
curl --location "$BASE_URL/api/method/landa.api.organization?id=AVE-069"
```

### Example Response

The response is always a list of dictionaries, like this:

```json
{
    "message": [
        {
            "id": "AVE-069",
            "organization_name": "Anglerverein \"R\u00f6deraue\" Gro\u00dfenhain e. V.",
            "website":"www.anglerverein-r\u00f6deraue.de",
            "register_number":null,
            "fishing_area": {
                "id":"D08",
                "area_name":
                "Riesa-Gro\u00dfenhain",
                "organization":"AVE"
            }
        }
    ]
}
```


## Water Body

Get a list of water bodies along with their main fish species and special provisions.

- `GET /api/method/landa.api.water_body`

    Parameters:

    - `id` (optional): return only data of the water body with this ID.
    - `fishing_area` (optional): return only water bodies in this fishing_area.

### Example Requests

> Remember set the environment variable `BASE_URL` to the URL of your LANDA instance. For example like this: `export BASE_URL=https://lvsa-landa.de`

Get all water bodies:

```bash
curl --location "$BASE_URL/api/method/landa.api.water_body"
```

Get a specific water body:

```bash
curl --location "$BASE_URL/api/method/landa.api.water_body?id=C09-110"
```

Get all water bodies in a specific fishing area:

```bash
curl --location "$BASE_URL/api/method/landa.api.water_body?fishing_area=C09"
```

### Example Response

The response is always a list of dictionaries, like this:

```json
{
    "message": [
        {
            "id": "C03-111",
            "title": "Stau Geringswalde",
            "fishing_area": "C03",
            "fishing_area_name": "Mittweida",
            "organization": "AVS",
            "organization_name": "Anglerverband S\u00fcdsachsen Mulde/Elster e. V.",
            "has_master_key_system": 0,
            "general_public_information": "bei Altgeringswalde, Parken nur mit Kopie des Erlaubnisscheines im Kfz",
            "current_public_information": "Das Gew\u00e4sser ist am Samstag den 23.10.2021 von 08:00 - 14:00 Uhr einer Jugendangelveranstaltung vorbehalten.",
            "size": 0.9,
            "size_unit": "ha",
            "fish_species": [
                { "id": "Hecht", "short_code": "H" },
                { "id": "Schleie", "short_code": "S" },
                { "id": "Karpfen", "short_code": "K" },
                { "id": "Rotauge (Pl\u00f6tze)", "short_code": "Pl" }
            ],
            "special_provisions": [
                { "id": "Behindertentauglich", "short_code": "H" }
            ],
            "geojson": {
                "type": "FeatureCollection",
                "features": []
            }
        }
    ]
}
```