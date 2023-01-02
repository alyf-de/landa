## 1. Create a site

```
bench new-site [site-name] --install-app erpnext
```

## 2. Complete the setup wizard

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


## 3. Install landa

> ERPNext must be already installed and the setup wizard completed before installing landa.

```bash
bench get-app https://github.com/realexperts/landa.git
bench --site [site-name] install-app landa
bench --site [site-name] migrate # currently necessary to get the "Member Count" chart
```

## Reinstallation (developers only)

> **Warning**: all site data will get deleted by the following commands

1. Uninstall landa and reinstall the site

    ```bash
    bench --site [site-name] uninstall-app landa
    bench --site [site-name] reinstall
    ```

2. Open your browser and complete the setup wizard, as described above.
3. Install landa, as described above.
