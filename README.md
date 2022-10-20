## LANDA

Datenmanagementsystem des Landesverbands Sächsischer Angler.

### Glossary

| German          | English               | Comment   |
|-----------------|-----------------------|-----------|
| Landesverband   | State Organization    | Root      |
| Regionalverband | Regional Organization | 1st Level |
| Verein          | Local Organization    | 2nd Level |
| Ortsgruppe      | Chapter               | 3rd Level |

### Installation 

#### 1. Create a site

```
bench new-site [site-name] --install-app erpnext
```

#### 2. Complete the setup wizard

Open the browser and complete the setup wizard, for example with the following values:

| Field                | Value                            | Comment |
|----------------------|----------------------------------|---------|
| Language             | English                          |         |
| Your Country         | Germany                          |         |
| Domains              | Non Profit (beta)                |         |
| Company Name         | Landesverband Sächsischer Angler |         |
| Company Abbreviation | LV                               |         |
| What does it do?     | Landesverband Sächsischer Angler |         |
| Bank Name            | Default Bank Account             |         |
| Chart of Accounts    | Standard with Numbers            |         |


#### 3. Install landa

> ERPNext must be already installed and the setup wizard completed before installing landa.

```bash
bench get-app https://github.com/realexperts/landa.git
bench --site [site-name] install-app landa
bench --site [site-name] migrate # currently necessary to get the "Member Count" chart
```

### Reinstallation (developers only)

> **Warning**: all site data will get deleted by the following commands

1. Uninstall landa and reinstall the site

    ```bash
    bench --site [site-name] uninstall-app landa
    bench --site [site-name] reinstall
    ```

2. Open your browser and complete the setup wizard, as described above.
3. Install landa, as described above.

### Data Import with pre-defined IDs

> This section became obsolete with https://github.com/frappe/frappe/pull/15238. Data Import should work out of the box now.

1. Temporarily enable naming by prompt

    1. Go to "Customize Form" for the related DocType
    2. In the "Naming" section, set autoname to "prompt" and click save

2. Do the data import
3. Manually set the naming series counter to the correct value

    a) Open the Regional Orgnaization to update the current number of it's Local Organizations
    b) Open Local Organization to Update the current number of it's Chapters or Members 

    Click on Menu > Update Naming Series

4. Disable naming by prompt

    1. Go to "Customize Form" for the related DocType
    2. In the "Naming" section, set autoname to "" (empty) and click save

### Create Demo Accounts

With the bench command `make-demo-accounts` you can create a **Member**, **Member Function** and **User** for every existing **Member Function Category**. Just specify an existing local organization:

```
bench --site landa make-demo-accounts AVS-001 
```

> The above example uses a site called "landa" and an organization called "AVS-001" as examples. Please replace these with your own values.

### Create a Template Item

1. Open the Item List and click "Add Item"
2. Click "Edit in Full Page"
3. Set the Item Name, for example "Erlaubnisschein"
4. Verify that the correct regional Organization is set in the "Company" field. For example, "Anglerverband Leipzig e. V."
5. Open the section "Variants"
6. Check "Has Variants"
7. Select "Variant Based On" = "Item Attribute"
8. Add the desired attributes to the list. For example, "Erlaubnisscheinart" or "Gültigkeitsjahr"
9. Choose the required Item Tax Template. For example, "Umsatzsteuer 19%"
10. Fill any additional fields (for example, "Description") that should get copied to all variants
11. Click the "Save" button on the top right

### API

- `/api/method/landa.api.organization`

    Return a list of organizations with ID, organization name, geojson, address and contact.

    Parameters:

    - `id` (optional): return only data of the organization with this ID.


### Deleting

When deleting a **LANDA Member**, this app ...

- Tries to delete the linked **User**.

    If the user cannot be deleted, it removes the link to this member and disables the user.

- Tries to delete all **Addresses** and **Contacts**, which are linked to this member only.
- Decrements the counter of the naming series, if this member was just created (has the highest number).

When deleting a **LANDA Member** and/or **User**, this app ...

- Removes rows linking to this user/member from all child tables
- Unsets all *optional* links to this user/member
- Deletes all documents containing a *mandatory* link to this user/member
