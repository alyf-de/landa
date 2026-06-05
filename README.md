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
- [Translation](docs/translation.md)

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

There's a daily scheduled job that deletes all **Users** that have been inactive for more than 18 months.

## License

LANDA – Datenmanagementsystem des Landesverband Sächsischer Angler e. V.
Copyright (C) 2022 ALYF GmbH and contributors.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
