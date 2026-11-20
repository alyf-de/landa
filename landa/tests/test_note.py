import frappe
from frappe.desk.doctype.note.note import mark_as_seen
from frappe.tests.utils import FrappeTestCase

DESK_USER = "note-reader@example.com"


class TestNote(FrappeTestCase):
	def setUp(self):
		if not frappe.db.exists("User", DESK_USER):
			user = frappe.new_doc("User")
			user.email = DESK_USER
			user.first_name = "Note Reader"
			user.send_welcome_email = 0
			user.append("roles", {"role": "Sales User"})
			user.insert(ignore_permissions=True)

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_desk_user_can_mark_public_note_as_seen(self):
		"""Every desk user gets the public notes on login and marks them as seen."""
		note = frappe.new_doc("Note")
		note.title = "Privacy Notice"
		note.public = 1
		note.notify_on_login = 1
		note.insert(ignore_permissions=True)

		frappe.set_user(DESK_USER)
		mark_as_seen(note.name)

		frappe.set_user("Administrator")
		note.reload()
		self.assertIn(DESK_USER, [row.user for row in note.seen_by])
