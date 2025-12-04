"""Delete Translation records that are identical to translations in PO files.

This patch removes Translation records from the database where source_text,
context, AND translated_text all match an entry in the PO files of landa,
frappe, or erpnext. These database records are redundant since the
gettext-based translation system will use the PO file translations.
"""

import frappe
from babel.messages.pofile import read_po


def execute():
	po_translations = set()

	# Collect all translations from PO files
	for app in ("landa", "frappe", "erpnext"):
		app_translations = get_po_translations(app, "de")
		print(f"Loaded {len(app_translations)} translations from {app}")
		po_translations.update(app_translations)

	if not po_translations:
		print("No PO translations found")
		return

	# Find and delete identical Translation records
	translations_to_delete = set()

	# Get all German translations from the database
	db_translations = frappe.get_all(
		"Translation",
		filters={"language": "de"},
		fields=["name", "source_text", "context", "translated_text"],
	)
	print(f"Found {len(db_translations)} German translations in database")

	for translation in db_translations:
		key = (
			translation.source_text,
			translation.context or None,
			translation.translated_text,
		)
		if key in po_translations:
			translations_to_delete.add(translation.name)

	if translations_to_delete:
		frappe.db.delete("Translation", {"name": ("in", translations_to_delete)})
		print(f"Deleted {len(translations_to_delete)} identical Translation records")
	else:
		print("No identical translations found to delete")

	frappe.db.commit()


def get_po_translations(app: str, locale: str) -> set[tuple[str, str | None, str]]:
	"""Get all (source_text, context, translated_text) tuples from a PO file."""
	translations = set()

	try:
		app_path = frappe.get_app_path(app)
	except Exception:
		# App not installed
		return translations

	from pathlib import Path

	po_path = Path(app_path) / "locale" / f"{locale}.po"

	if not po_path.exists():
		return translations

	with open(po_path, "rb") as f:
		catalog = read_po(f)

	for message in catalog:
		if not message.id or not message.string:
			continue
		# Normalize empty context to None (same as DB side)
		translations.add((message.id, message.context or None, message.string))

	return translations
