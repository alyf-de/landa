## LANDA

Datenmanagementsystem des Landesverbands Sächsischer Angler.

### Data Import with pre-defined IDs

1. Temporarily enable naming by prompt

    1. Go to "Customize Form" for the related DocType
    2. In the "Naming" section, set autoname to "prompt" and click save

2. Do the data import
3. Manually set the naming series counter to the correct value

```
In [1]: frappe.db.sql("UPDATE `tabSeries` SET current = %(current)s WHERE name=%(prefix)s", {"prefix": "MY-SERIES-001-", "current": 17})
Out[1]: ()

In [2]: frappe.db.commit()
```

4. Disable naming by prompt

    1. Go to "Customize Form" for the related DocType
    2. In the "Naming" section, set autoname to "" (empty) and click save
