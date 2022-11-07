import frappe


def execute():
    def value_not_set(dict, field):
        return len(dict) > 0 and (1 not in [d[field] for d in dict])

    contacts = frappe.get_list("Contact", as_list=True)
    for contact in contacts:
        # if no email_id is set as primary for a contact, set the first email_id as primary
        contact_emails = frappe.get_list(
            "Contact Email",
            filters={"parent": contact[0]},
            fields=["name", "is_primary"],
        )
        if value_not_set(contact_emails, "is_primary"):
            frappe.db.set_value(
                "Contact Email", contact_emails[0]["name"], "is_primary", 1
            )
        # if no phone is set as primary mobile or primary phone for a contact,
        # set all phones as primary phone or primary phone according to the first digits of the phone number
        contact_phones = frappe.get_list(
            "Contact Phone",
            filters={"parent": contact[0]},
            fields=["name", "phone", "is_primary_mobile_no", "is_primary_phone"],
        )
        if value_not_set(contact_phones, "is_primary_mobile_no") and value_not_set(
            contact_phones, "is_primary_phone"
        ):
            for contact_phone in contact_phones:
                cleared_number = "".join(filter(str.isdigit, contact_phone["phone"]))
                if (
                    cleared_number[:2] == "01"
                    or cleared_number[:3] == "491"
                    or cleared_number[:5] == "00491"
                ):
                    frappe.db.set_value(
                        "Contact Phone",
                        contact_phone["name"],
                        "is_primary_mobile_no",
                        1,
                    )
                else:
                    frappe.db.set_value(
                        "Contact Phone", contact_phone["name"], "is_primary_phone", 1
                    )
