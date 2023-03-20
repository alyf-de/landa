import frappe
from frappe.tests.utils import FrappeTestCase
from landa.utils import remove_from_table


class TestUtils(FrappeTestCase):
	def test_remove_from_table(self):
		"""Create a new Note, add a user to the seen_by table, then remove them"""
		note = frappe.new_doc("Note")
		note.title = "Test Note"
		note.extend("seen_by", [{"user": "Administrator"}, {"user": "Guest"}])
		note.save(ignore_permissions=True)

		self.assertEqual(len(note.seen_by), 2)

		remove_from_table("Note Seen By", "user", "Guest")

		note.reload()
		self.assertEqual(len(note.seen_by), 1)
