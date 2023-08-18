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

Get a list of water bodies along with their main fish species and special provisions. Water bodies that are inactive or have _Display In Fishing Guide_ disabled, are not included in the response.

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

> Only public files attached to Water Bodies are returned via the API. They are all absolute links to the resource.

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
            "guest_passes_available": 0,
            "general_public_information": "bei Altgeringswalde, Parken nur mit Kopie des Erlaubnisscheines im Kfz",
            "current_public_information": "Das Gew\u00e4sser ist am Samstag den 23.10.2021 von 08:00 - 14:00 Uhr einer Jugendangelveranstaltung vorbehalten.",
            "size": 0.9,
            "size_unit": "ha",
            "status": "Verbandsvertragsgewässer",
            "fish_species": [
                "Hecht",
                "Schleie",
                "Karpfen",
                "Rotauge (Pl\u00f6tze)",
            ],
            "special_provisions": [
                { "id": "Behindertentauglich", "short_code": "H" }
            ],
            "organizations": [
                {
                    "id": "AVS-001",
                    "organization_name": "AV \"Aktive Angler\" e. V."
                }
            ],
            "geojson": {
                "type": "FeatureCollection",
                "features": []
            },
            "files": [
                "https://lvsa-landa.de/files/image-1.jpg",
                "https://lvsa-landa.de/files/image-2.jpg",
                "https://lvsa-landa.de/files/doc-1.pdf"
            ]
        }
    ]
}
```

## Fish Species

Get a list of fish species along with their data.

- `GET /api/method/landa.api.fish_species`

    Parameters:

    - `id` (optional): return only data of the Fish Species with this ID.

### Example Requests

> Remember to set the environment variable `BASE_URL` to the URL of your LANDA instance. For example like this: `export BASE_URL=https://lvsa-landa.de`

Get all Fish Species:

```bash
curl --location "$BASE_URL/api/method/landa.api.fish_species"
```

Get a specific Fish Species:

```bash
curl --location "$BASE_URL/api/method/landa.api.fish_species?id=Flounder"
```

### Example Response

The response is always a list of dictionaries, like this:

```json
{
    "message": [
        {
            "id": "Flounder",
            "short_code": "FLNDR",
            "scientific_name": "Platichthys flesus",
            "close_season": "Winter",
            "minimum_size": "20",
            "general_fishing_limit": "80",
            "special_fishing_limit": "160",
            "traits": "Shiny silver fish",
            "image": "https://lvsa-landa.de/files/fish-flounder.webp"
        }
    ]
}
```