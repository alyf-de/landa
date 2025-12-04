In general, translations are managed using PO files in the `landa/locale/` directory. PO files exclude strings that are already translated in Frappe or ERPNext.

To update translations, run the following commands:

```bash
# ERPNext v15 does not come with a pot file, but we need it to exclude existing translations.
bench generate-pot-file --app erpnext

# Generate POT file for LANDA
bench generate-pot-file --app landa

# Update PO files from POT files
bench update-po-files --app landa
```

To override translations from Frappe or ERPNext, we **Translation** records in the database and export them as fixtures.

```bash
bench export-fixtures --app landa
```
