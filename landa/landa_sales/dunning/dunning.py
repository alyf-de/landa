from frappe.utils import getdate


def autoname(doc, event):
	"""Create Company-specific Dunning name."""
	from landa.utils import get_new_name

	year = str(getdate(doc.posting_date).year)
	doc.name = get_new_name("MAHN", doc.company, "Dunning", year)
