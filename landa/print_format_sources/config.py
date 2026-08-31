# Copyright (c) 2026, ALYF GmbH and Contributors
# See license.txt

"""Source-of-truth mapping for **Print Format** docs synced by `print_formats.py`.

Per format:

- key: the **Print Format** name (shown in Desk)
- `DocType`: the DocType the format prints (required); maps to the Print Format
  `doc_type` field
- `template`: `*.jinja` filename next to this module (required)
- `fields`: optional dict of additional **Print Format** field overrides, e.g.
  `module`, `pdf_generator`, `default_print_language`, margins, page number

All formats share one stylesheet: `landa/public/scss/landa_print_format.bundle.scss`,
compiled by `bench build` and copied into every doc on migrate. Per-format tweaks
belong in a `<style>` block in that format's `.jinja`.
"""

from __future__ import annotations

CSS_BUNDLE = "landa_print_format.bundle.css"

# Every format prints German documents in the LANDA letterhead.
COMMON_FIELDS = {
	"default_print_language": "de",
	"font": "Default",
}

PRINT_FORMATS: dict[str, dict] = {
	"SO DIN Addressfield": {
		"DocType": "Sales Invoice",
		"template": "so_din_addressfield.jinja",
		"fields": {**COMMON_FIELDS, "module": "LANDA Sales"},
	},
	"MF DIN Addressfield": {
		"DocType": "Sales Invoice",
		"template": "mf_din_addressfield.jinja",
		"fields": {**COMMON_FIELDS, "module": "LANDA Sales"},
	},
	"LVSA DIN-Rechnung": {
		"DocType": "Sales Invoice",
		"template": "lvsa_din_rechnung.jinja",
		"fields": {**COMMON_FIELDS, "module": "LANDA Sales"},
	},
	"Beitragsabrechnung": {
		"DocType": "Statement of Fees and Payments",
		"template": "beitragsabrechnung.jinja",
		"fields": {**COMMON_FIELDS, "module": "LANDA Sales"},
	},
	"Zahlungsbeleg": {
		"DocType": "Payment Entry",
		"template": "zahlungsbeleg.jinja",
		"fields": {**COMMON_FIELDS, "module": "LANDA Sales"},
	},
	"DN DIN Addressfield": {
		"DocType": "Delivery Note",
		"template": "dn_din_addressfield.jinja",
		"fields": {**COMMON_FIELDS, "module": "LANDA Stock"},
	},
}
