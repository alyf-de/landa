from frappe.custom.doctype.property_setter.property_setter import delete_property_setter


def execute():
	delete_property_setter("Delivery Note Item", property="columns", field_name="serial_no")
