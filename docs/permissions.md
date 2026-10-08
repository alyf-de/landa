Prerequisites:

- [Organizations and Members](organizations-and-members.md)

A **LANDA Member** always belongs to a Local Organization or to a Local Group. By default, new **Users** are restricted to see only data of their own **Organization** and **LANDA Member**. For example, a member AVL-001-001 has the following **User Permissions** by default:

- _Allow **Organization** for value "AVL-001"_, and
- _Allow **LANDA Member** for value "AVL-001-001"_.

A **Member Function Category** is similar to a **Role Profile** in that it defines the roles a user should get. But it may also define relaxed **User Permissions** (access to lower level organizations, access to member data). In a **Member Function Category** we can define

- the required roles,
- at which level in the **Organization** tree a member can act, and
- whether they can view/edit the personal data of other members.

A **Member Function** assigns a **Member Function Category** to a **LANDA Member**, for a specific period of time. When a **Member Function** is enabled, the member/user gets the additional permissions defined in the **Member Function Category**. When a **Member Function** is disabled, the member/user loses the additional permissions defined in the **Member Function Category**.

When there are multiple active **Member Function Categories** for a member/user, they get the highest permissions possible. This means the union of all roles, access at the maximum allowed level, and access to member data, if any.

If a member/user is allowed to view/edit the personal data of other members, the default **User Permission** _Allow **LANDA Member** for value "AVL-001-001"_ will be removed.

If a member/user is allowed access to lower level organizations, the default **User Permission** _Allow **Organization** for value "AVL-001"_ will be adjusted. For example, to _Allow **Organization** for value "AVL"_.

The data model:

```mermaid
erDiagram
    USER |o--o| LANDA-MEMBER : belongs-to
    LANDA-MEMBER }o--|| ORGANIZATION : belongs-to
    LANDA-MEMBER ||--o{ MEMBER-FUNCTION : has
    MEMBER-FUNCTION }o--|| MEMBER-FUNCTION-CATEGORY : has-type
    MEMBER-FUNCTION-CATEGORY }o--o{ ROLE : grants
    USER }o--o{ ROLE : has
```

What happens when a **Member Function** becomes active or inactive (on save, on delete, or by the daily job for expired functions). This only applies if the member has an enabled **User**.

```mermaid
flowchart TD
    A[Member Function becomes active / inactive] --> B[Collect all active Member Function Categories of the member]
    B --> C[Roles: add the category's roles, or remove the roles<br/>that no other active category grants. LANDA Member is always kept.]
    B --> D{Any category with<br/>member administration?}
    D -- yes --> E[Remove User Permission on LANDA Member]
    D -- no --> F[Restrict to own LANDA Member]
    B --> G[Highest access level of all categories]
    G --> H[Replace User Permission on Organization<br/>with the member's ancestor at that level]
```

Example for member "AVL-001-001" of organization "AVL-001":

| Active Member Functions | Roles | User Permissions |
|---|---|---|
| None | "LANDA Member" | **Organization** "AVL-001", **LANDA Member** "AVL-001-001" |
| One category with _Access Level_ "Regional Organization" and _Member Administration_ | "LANDA Member" + roles of the category | **Organization** "AVL" |


### Tag permissions

We want to restrict tags to Organizations. A user is supposed to see only tags created by people in the same **Organization**.

The default way to achieve this would be adding a link field from **Tag** to **Organization**. Then the user permissions would take care of the rest. However, for tags, the ID is also the visible label. This means that two organizations would not be able to use the same tag.

To prevent this, we added a table named **Tag Organization** to the **Tag** doctype. When a new tag is created, the creator's organization is added to this table. We also added a custom permission query which checks if the user's organization is in this table. This way users can only see tags created by people in the same organization.

See https://github.com/alyf-de/landa/pull/254 for details.

### Monitoring

Usually, most users should be restricted to seeing data of their own organization only. However, some users are allowed to see data of other organizations.

For monitoring users with high permissions, we created a report named **LANDA Power Users**. It shows all users with high permissions, and which organizations they are allowed to see. Excluded are the default users **Administrator** and **Guest**. Also, users who are members of a regional organization (e.g. AVL-000) and have permissions for that regional organization (e.g. AVL) are excluded.
