# UI tests

The UI tests run in a real browser with [Playwright](https://playwright.dev). They cover form behavior that the server tests cannot reach, for example the client script of **Sales Order**.

The Frappe Framework supplies the runner (`bench run-ui-tests`), the Playwright installation, and the helpers in `apps/frappe/playwright/support`. This app contains only the configuration, the specs and the test data:

- `playwright.config.js`: Playwright configuration.
- `playwright/support/index.js`: passes on the helpers of Frappe.
- `playwright/tests/*.spec.js`: the specs.
- `landa/tests/ui_test_helpers.py`: server methods that create the test data.

## Run the tests

Prerequisites:

- The site is a test site. The tests create organizations, members, users and items on it.
- The bench runs with `bench start`. The test data methods are available only on a development server.
- The browser can open the site URL that `bench --site $SITE execute frappe.utils.get_url` prints. If necessary, add the site name to `/etc/hosts` or set `host_name` in the site config.
- The password of "Administrator" is "admin", or the site config contains `admin_password`.

Run all specs without a visible browser:

```bash
bench --site $SITE run-ui-tests landa --headless
```

Without `--headless`, the Playwright UI opens. There you can select specs and watch each step.

The first run installs Playwright and Chromium into the Frappe app.

## Write a test

1. Create the data that the test needs with a method in `landa/tests/ui_test_helpers.py`. Decorate the method with `@whitelist_for_tests`. Make it safe to call more than once.
2. Call the method in `test.beforeAll` with the `admin` fixture.
3. Log in with `desk.login(user)`. Each spec starts as a guest, because each user of this app needs a **LANDA Member**. The password of the test users is the administrator password.
4. Wait for a visible result, not for a fixed time.

`playwright/tests/sales_order.spec.js` is an example.
