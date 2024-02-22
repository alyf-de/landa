## 0. Set up the correct frappe branch

Currently we rely on a [custom frappe branch](https://github.com/alyf-de/frappe/tree/landa-version-13) that adds a couple of fixes to `version-13`:

```
cd apps/frappe
git remote add alyf https://github.com/alyf-de/frappe
git checkout --track alyf/landa-version-13
```

## Set up CORS

To allow the Angelatlas web-apps to access the API, add the following to `sites/common_site_config.json`:

```json
{
    "..." : "...",
    "allow_cors": [
        "https://angelatlas.devid.net",
        "https://www.angelatlas-sachsen.de/"
        "https://angelatlas-sachsen.de/"
    ]
}
```

Also, for embedding static (uploaded) files and icons, we need to modify the nginx configuration in `config/nginx.conf`

```
# Define the variable $cors_origin to be the value of the header "Origin" if it
# matches one of the allowed origins, otherwise empty.
map $http_origin $cors_origin {
    default "";
    https://www.angelatlas-sachsen.de $http_origin;
    https://angelatlas-sachsen.de $http_origin;
    https://angelatlas.devid.net $http_origin;
}

server {
    ...

    location / {
        rewrite ^(.+)/$ $1 permanent;
        rewrite ^(.+)/index\.html$ $1 permanent;
        rewrite ^(.+)\.html$ $1 permanent;

        # Allow CORS for static files
        add_header Access-Control-Allow-Origin $cors_origin;
        add_header Access-Control-Allow-Methods "GET, OPTIONS";

        location ~* ^/files/.*.(htm|html|svg|xml) {
            add_header Content-disposition "attachment";

            # Allow CORS again, specifically for the above filetypes
            add_header Access-Control-Allow-Origin $cors_origin;
            add_header Access-Control-Allow-Methods "GET, OPTIONS";

            try_files /$site_name_eqzecbv/public/$uri @webserver;
        }

        try_files /$site_name_eqzecbv/public/$uri @webserver;
    }

    ...
}
```

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
bench get-app https://github.com/alyf-de/landa
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
