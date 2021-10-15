
def autoname(doc, event):
	"""Create Company-specific Sales Invoice name."""
	from landa.utils import get_new_name

	if doc.is_return:
		doc.name = get_new_name("GUTS", doc.company, "Sales Invoice")
	else:
		doc.name = get_new_name("RECH", doc.company, "Sales Invoice")
