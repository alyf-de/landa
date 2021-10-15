

def after_insert(contact, event):
	"""
	Delete Contact if it's linked to User.

	Frappe automatically creates a Contact for each User. For data protection
	reasons we don't want this. Therefore we delete the contact again.
	"""
	if contact.user:
		contact.delete()
