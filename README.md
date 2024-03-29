## LANDA

Datenmanagementsystem des Landesverbands Sächsischer Angler.

- [Installation](docs/installation.md)
- [Organizations and Members](docs/organizations-and-members.md)
- [Permissions](docs/permissions.md)
- [Data Import](docs/data-import.md)
- [CLI](docs/cli.md)

   How to create demo accounts or import GeoJSON files using the command line interface.

- [System Updates](docs/system-updates.md)
- [API](docs/api.md)

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
