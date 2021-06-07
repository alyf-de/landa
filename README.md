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

```
bench get-app https://github.com/realexperts/landa.git
bench --site [site-name] install-app landa
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
