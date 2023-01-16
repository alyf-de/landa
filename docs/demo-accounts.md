### Create Demo Accounts

This app provide a bench command `make-demo-accounts`. This is useful for testing permissions. You can use it to create a **Member**, **Member Function** and **User** for every existing **Member Function Category**, in an existing local organization.

Prerequisites:

1. Create a [Local Organization](organizations-and-members.md)
2. Define some [Member Function Categories](permissions.md)

Now you can run the following command (replace `$SITE` and `$ORGANIZATION` with your specific values):

```bash
bench --site $SITE make-demo-accounts $ORGANIZATION
```
