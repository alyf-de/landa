# Tree structure

**Organizations** are structured as a tree:

- Organization
    - Organization
        - Organization
            - Organization
                - LANDA Member
            - ...
        - Organization
            - LANDA Member
        - ...
    - ...

A **LANDA Member** always belongs to a _leaf_ in the **Organization** tree. An **Organization** that is a group cannot have any members.

The level of an **Organization** in the tree determines if they are regarded as a State Organization (0), Regional Organizations (1), Local Organization (2) or Local Group (3).

- State Organization
    - Regional Organization
        - Local Organization
            - Local Group
                - LANDA Member
            - ...
        - Local Organization
            - LANDA Member
        - ...
    - ...

A State Organization can have multiple Regional Organizations. Each Regional Organization can have multiple Local Organizations. Each Local Organization can have either Local Groups or members (but not both). Each Local group can have members (but no child organizations). A **LANDA Member** always belongs to a Local Organization or to a Local Group (a _leaf_ in the **Organization** tree).

# Naming

State and regional organizations are named by short codes, for example, "LV", "AVL", etc.

Local Organizations, Local Groups and members are named by a naming series based on their parents name, for example "AVL-001" (Local Organization), "AVL-001-09" (Local Group), or "AVL-001-0001" (member of a Local Organization).

This means there can be a different number of instances on each level:

- State Organization (1..1)
    - Regional Organization (0..n)
        - Local Organization (0..999)
            - [ Local Group (0..99) ]
                - LANDA Member (0..9999)

For example, an **Organization** tree might look like this:

- LV
    - AVL
        - AVL-001
        - AVL-002
            - AVL-002-01
            - AVL-002-02
            - ...
        - ...
    _ ...

The **LANDA Members** belonging to **Organization** AVL-001 will be named like this:

- AVL-001-0001
- AVL-001-0002
- ...

The **LANDA Members** belonging to **Organization** AVL-002-01 will be named like this:

- AVL-002-01-0001
- AVL-002-01-0002
- ...

### German terms

| German            | English               | Comment      |
|-------------------|-----------------------|--------------|
| Landesverband     | State Organization    | Level 0      |
| Regionalverband   | Regional Organization | Level 1      |
| Verein            | Local Organization    | Level 2      |
| Ortsgruppe        | Local Group           | Level 3      |
| Mitglied          | LANDA Member          | Level 3 or 4 |
| Mitgliedsfunktion | Member Function       |              |
