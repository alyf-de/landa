## LANDA

Datenmanagementsystem des Landesverbands Sächsischer Angler.

## Glossar

Landesverband: State Organization (Wurzel)
Regionalverband: Regional Organization (1. Ebene)
Verein: Local Organization (2. Ebene)
Ortsgruppe: Chapter (3. Ebene)

### Installation 

> ERPNext muss bereits installiert und über den Setup-Wizard **eingerichtet** sein, bevor diese App installiert werden kann.

`bench --site [site-name] install-app landa`

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

### Create Demo Accounts

With the bench command `make-demo-accounts` you can create a **Member**, **Member Function** and **User** for every existing **Member Function Category**. Just specify an existing local organization:

```
bench --site landa make-demo-accounts AVS-001 
```

> The above example uses a site called "landa" and an organization called "AVS-001" as examples. Please replace these with your own values.
