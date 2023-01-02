## Data Import with pre-defined IDs

> This section became obsolete with https://github.com/frappe/frappe/pull/15238. Data Import should work out of the box now.

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
