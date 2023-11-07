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
curl --location "$BASE_URL/api/method/landa.api.fish_species?id=Bachforelle"
```

### Example Response

The response is always a list of dictionaries, like this:

```json
{
  "message": [
    {
      "id": "Bachforelle",
      "short_code": "Bf",
      "scientific_name": "Salmo trutta fario",
      "close_season": "01.10-30.04.",
      "minimum_size": "28 cm",
      "general_fishing_limit": "2",
      "special_fishing_limit": "3",
      "traits": "Fettflosse mit roten Tupfen\nK\u00f6rper lang gestreckt, seitlich abgeflacht, hoher\nSchwanzstiel\nrote und br\u00e4unlich-schwarze Tupfen\nendst\u00e4ndiges Maul, Maulspalte reicht bis hinter Auge\nmaximal 90 cm lang, dann \u00fcber 10 kg schwer",
      "wikipedia_link": "http://de.wikipedia.org/wiki/Bachforelle",
      "image": "https://lvsa-landa.de/files/4_big.png",
      "thumbnail": "https://lvsa-landa.de/files/4_small.png"
    }
  ]
}
```

## Water Body Rules, Privacy Policy and Imprint

Get a the fishing rules applicable to all water bodies.

- `GET /api/method/landa.api.water_body_rules`

### Example Requests

> Remember to set the environment variable `BASE_URL` to the URL of your LANDA instance. For example like this: `export BASE_URL=https://lvsa-landa.de`

Get Water Body Rules:

```bash
curl --location "$BASE_URL/api/method/landa.api.legal"
```

### Example Response

The response is always an object with HTML strings, like this:

```json
{
    "message": {
        "water_body_rules": "<div class=\"ql-editor read-mode\"><h1>Gew\u00e4sserordnung</h1><p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p><p><br></p><table class=\"table table-bordered\"><tbody><tr><td data-row=\"row-kiex\"><strong>Bild</strong></td><td data-row=\"row-kiex\"><strong>Fischart</strong></td></tr><tr><td data-row=\"row-z953\"><img src=\"/files/1_big.png\"></td><td data-row=\"row-z953\">Aal</td></tr><tr><td data-row=\"insert-table\"><img src=\"/files/7_big.png\"></td><td data-row=\"insert-table\">Barsch</td></tr></tbody></table></div>",
        "privacy_policy": "<div class=\"ql-editor read-mode\"><h1>Datenschutz</h1><p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p></div>",
        "imprint": "<div class=\"ql-editor read-mode\"><h1>Impressum</h1><p>Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.</p></div>"
    }
}
```

The legth of each text field is limited to around 8000 words.

## Change Log

Get a list of changes to the water bodies and fish species.

- `GET /api/method/landa.api.change_log`

    Parameters:

    - `from_datetime` (required)

        Returns only changes that happened after this datetime. Format: `YYYY-MM-DD HH:MM:SS:SSSS`


Events covered by the change log are:

- Water Body, Fish Species
    - Created
    - Modified
    - Deleted

### Example Request

```bash
curl --location "$BASE_URL/api/method/landa.api.change_log?from_datetime=2023-01-01 00:00:00:0000"

# the time part is optional
curl --location "$BASE_URL/api/method/landa.api.change_log?from_datetime=2023-01-01"
```

### Example Response

```json
{
  "message": [
    {
      "doctype": "Water Body",
      "docname": "D08-201",
      "event": "Deleted",
      "datetime": "2023-02-02 15:48:07.841290"
    },
    {
      "doctype": "Water Body",
      "docname": "L09-108",
      "event": "Modified",
      "datetime": "2023-02-22 14:43:46.832560",
      "changes": { "organizations": null }
    },
    {
      "doctype": "Water Body",
      "docname": "L09-108",
      "event": "Modified",
      "datetime": "2023-03-20 13:28:52.630048",
      "changes": { "organizations": null }
    },
    {
      "doctype": "Water Body",
      "docname": "L10-230",
      "datetime": "2023-05-02 11:35:42.709453",
      "event": "Modified",
      "changes": { "current_public_information": "Testinfo" }
    },
    {
      "doctype": "Water Body",
      "docname": null,
      "event": "Modified",
      "datetime": "2023-05-10 09:16:29.221310",
      "changes": { "organizations": null }
    },
    {
      "doctype": "Fish Species",
      "docname": "\u00c4sche",
      "datetime": "2023-05-30 19:12:50.820108",
      "event": "Modified",
      "changes": { "image": "/files/a\u0308sche.png" }
    },
    {
      "doctype": "Fish Species",
      "docname": "Aal",
      "datetime": "2023-05-30 19:12:55.175626",
      "event": "Modified",
      "changes": { "image": "/files/aal.png" }
    },
    {
      "doctype": "Water Body",
      "docname": "D09-205",
      "datetime": "2023-06-06 15:24:17.019050",
      "event": "Modified",
      "changes": { "blacklisted_fish_species": null }
    },
    {
      "doctype": "Water Body",
      "docname": "L10-236",
      "datetime": "2023-06-07 12:53:53.712910",
      "event": "Modified",
      "changes": { "title": "Elsterbecken" }
    },
    {
      "doctype": "Water Body",
      "docname": "L09-108",
      "event": "Modified",
      "datetime": "2023-08-01 10:43:42.442427",
      "changes": { "organizations": null }
    }
  ]
}
```