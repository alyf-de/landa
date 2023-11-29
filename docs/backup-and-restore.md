## Restore a Backup

> Note: this guide shows only the essential steps. It assumes that you have experience setting up _Frappe Framework_ sites. For a production setup, you'll need additional work to setup a server, TLS certificates, etc. This varies greatly depending on the particular server and is out of scope for this guide.

You should have the following backup files:

* `20240101_000000-lvsa-landa_de-site_config_backup.json`
* `20240101_000000-lvsa-landa_de-private-files.tar`
* `20240101_000000-lvsa-landa_de-files.tar`
* `20240101_000000-lvsa-landa_de-database.sql.gz`

> Note: the datetime in the filenames is just an example. The actual datetime is the time when the backup was created.

On a new server, install frappe-bench and other prerequisites like MariaDB and Node. Then initializa a new bench:

```bash
bench init --frappe-branch version-13 --python python3.8 frappe-bench
```

Switch to our custom frappe branch:

```bash
cd apps/frappe
git remote add alyf-de https://github.com/alyf-de/frappe.git -t landa-version-13
git fetch alyf-de
git checkout --track alyf-de/landa-version-13
```

Get ERPNext:

```bash
cd ../..
bench get-app erpnext --branch version-13
```

Get Landa:

```bash
bench get-app https://github.com/alyf-de/landa.git --branch version-13
```

Create a new site:

```bash
bench new-site lvsa-landa.de
```

Copy the contents of your site config backup into the new `site_config.json` file. Please copy all contents except the `"db_name"` and `"db_password"` keys. These should remain as they are in the new `site_config.json` file.

Restore the database and uploaded files (this will take a couple of minutes):

```bash
bench --site lvsa-landa.de restore 20240101_000000-lvsa-landa_de-database.sql.gz --with-public-files 20240101_000000-lvsa-landa_de-files.tar --with-private-files 20240101_000000-lvsa-landa_de-private-files.tar
```

Make sure your bench is running.

Migrate the database to match your current code version:

```bash
bench --site lvsa-landa.de migrate
```

That's it! You should now be able to access your site and login with your old credentials.
