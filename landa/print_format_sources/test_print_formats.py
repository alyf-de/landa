# Copyright (c) 2026, ALYF GmbH and Contributors
# See license.txt

"""Self-check for the print format builder. Run: python -m landa.print_format_sources.test_print_formats"""

from pathlib import Path

from .config import PRINT_FORMATS
from .print_formats import build_print_format_docs

HERE = Path(__file__).resolve().parent
CSS = "/* built bundle */"


def demo() -> None:
	docs = build_print_format_docs(HERE, CSS)
	assert len(docs) == len(PRINT_FORMATS), docs

	by_name = {d["name"]: d for d in docs}
	assert set(by_name) == set(PRINT_FORMATS)

	for name, spec in PRINT_FORMATS.items():
		doc = by_name[name]
		assert doc["doctype"] == "Print Format"
		assert doc["doc_type"] == spec["DocType"]
		# Exported .json would land in the module's app; sources stay the only copy.
		assert doc["standard"] == "No", name
		assert doc["html"] == (HERE / spec["template"]).read_text(encoding="utf-8"), name
		# One authoritative bundle: no format carries its own stylesheet.
		assert doc["css"] == CSS, name

	print(f"ok: {len(docs)} print formats build cleanly")


if __name__ == "__main__":
	demo()
