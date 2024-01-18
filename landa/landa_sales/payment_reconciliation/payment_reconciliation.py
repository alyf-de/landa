from landa.utils import get_current_member_data


def onload(doc, event):
	"""Set the user's company in order to circumvent strict user permissions."""
	member_data = get_current_member_data()
	doc.company = member_data.company
	doc.party_type = "Customer"
