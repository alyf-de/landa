import frappe

DEFAULT_FIELDS = (
	("default_billing_address", "Address"),
	("default_shipping_address", "Address"),
	("default_billing_contact", "Contact"),
	("default_shipping_contact", "Contact"),
)


def execute():
	"""Link default Address/Contact records back to their Customer.

	Customer can point at an Address or Contact via default_billing_* /
	default_shipping_* without a reverse row in that document's `links` table.
	Sales Invoice (and other sales docs) then reject the Address/Contact because
	they validate that it belongs to the Customer via Dynamic Link.
	"""
	seen = set()
	for fieldname, parenttype in DEFAULT_FIELDS:
		for customer, customer_name, parent in _missing_links(fieldname, parenttype):
			key = (parenttype, parent, customer)
			if key in seen:
				continue
			seen.add(key)
			_add_link(parenttype, parent, customer, customer_name)


def _missing_links(fieldname, parenttype):
	Customer = frappe.qb.DocType("Customer")
	Link = frappe.qb.DocType("Dynamic Link")
	linked = getattr(Customer, fieldname)

	return (
		frappe.qb.from_(Customer)
		.left_join(Link)
		.on(
			(Link.parent == linked)
			& (Link.parenttype == parenttype)
			& (Link.link_doctype == "Customer")
			& (Link.link_name == Customer.name)
		)
		.select(Customer.name, Customer.customer_name, linked)
		.where(linked.isnotnull())
		.where(linked != "")
		.where(Link.name.isnull())
		.run()
	)


def _add_link(parenttype, parent, customer, customer_name):
	if not frappe.db.exists(parenttype, parent):
		return

	indexes = frappe.get_all(
		"Dynamic Link",
		filters={"parenttype": parenttype, "parent": parent},
		pluck="idx",
	)

	frappe.get_doc(
		{
			"doctype": "Dynamic Link",
			"parenttype": parenttype,
			"parent": parent,
			"parentfield": "links",
			"idx": max(indexes, default=0) + 1,
			"link_doctype": "Customer",
			"link_name": customer,
			"link_title": customer_name or customer,
		}
	).insert(ignore_permissions=True)
