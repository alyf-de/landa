from frappe.custom.doctype.property_setter.property_setter import delete_property_setter

ADDRESS_FETCH_FIELDS = (
	("Sales Invoice", "customer_address"),
	("Sales Invoice", "shipping_address_name"),
	("Delivery Note", "customer_address"),
	("Delivery Note", "shipping_address_name"),
)


def execute():
	for doctype, fieldname in ADDRESS_FETCH_FIELDS:
		delete_property_setter(doctype, property="fetch_from", field_name=fieldname)
		delete_property_setter(doctype, property="fetch_if_empty", field_name=fieldname)
