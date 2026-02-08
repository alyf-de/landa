## Stocking Measure Import

> PR: https://github.com/alyf-de/landa/pull/293

### Business Case

A **Stocking Measure** (Besatzmaßnahme) records one fish stocking event: a specific fish species/type stocked into a specific water body on a given date. In practice, multiple species are stocked into the same water body at once, so users had to create each record individually — repetitive and error-prone.

**Stocking Measure Import** provides a bulk-entry form: the user selects a water body and a year once, then fills a table with multiple fish species/types. On save, each row becomes its own **Stocking Measure** record.

### Approach: Virtual DocType

The feature is implemented as a virtual DocType. This means:

- There is no database table for the form itself.
- The form is generated fresh on every load (defaults from the current user's organization and today's date).
- On save, `db_insert` / `db_update` do not write to the database — instead they loop over the child table and create one **Stocking Measure** per row.
- After save, the items table is cleared so the user can immediately enter the next batch.

This pattern is similar to the existing **Member Data Import** virtual DocType.

The client script always routes to an "existing" form, even when the user clicks "create new". On this form, the sidebar and footer (comments, attachments, etc.) are actively hidden because they are not relevant for this create-only form. This keeps a consistent create-only UI. The header fields (organization, water body, year, date) are preserved across saves, so the user does not have to re-enter them for each batch.


### DocTypes

Three new virtual DocTypes were introduced:

DocType | Role
---|---
 **Stocking Measure Import** | Main form with header fields and two child tables
 **Stocking Measure Import Item** | Editable child table: one row per fish species to import
 **Stocking Measure Import History** | Read-only child table: Shows **Stocking Measures** created by the current user in the last 24 hours.
