import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

from landa.water_body_management.change_log import ChangeLog


class TestChangeLog(FrappeTestCase):
	def setUp(self):
		self.from_datetime = now_datetime()
		self.water_body_name = (
			frappe.get_doc(
				{
					"doctype": "Water Body",
					"title": "Change Log Test",
					"number": "999",
					"fishing_area": frappe.get_all("Fishing Area", pluck="name", limit=1)[0],
					"status": "Allgemeines Angelgewässer",
					"is_active": 1,
					"display_in_fishing_guide": 1,
				}
			)
			.insert()
			.name
		)

	def tearDown(self):
		frappe.db.rollback()

	def update_water_body(self, **values):
		# Load a fresh doc like a real request does. Tests skip Versions by default.
		water_body = frappe.get_doc("Water Body", self.water_body_name)
		water_body.update(values)
		water_body.save(ignore_version=False)

	def get_events(self):
		return [
			log
			for log in ChangeLog().get_logs(from_datetime=self.from_datetime)
			if log["docname"] == self.water_body_name
		]

	def test_public_water_body(self):
		self.update_water_body(title="Change Log Test 2", is_property_water_body=1)

		created, modified = self.get_events()
		self.assertEqual(created["event"], "Created")
		self.assertEqual(modified["changes"], {"title": "Change Log Test 2"})

	def test_hidden_water_body(self):
		self.update_water_body(display_in_fishing_guide=0)
		self.update_water_body(title="Secret Title")

		# Creation and changes are hidden, only the removal is reported
		events = self.get_events()
		self.assertEqual([event["event"] for event in events], ["Deleted"])
		self.assertNotIn("changes", events[0])

	def test_water_body_made_public_again(self):
		self.update_water_body(is_active=0)
		self.update_water_body(is_active=1)

		# The current state decides, so both visibility changes are reported as created
		events = self.get_events()
		self.assertEqual([event["event"] for event in events], ["Created", "Created", "Created"])

	def test_deleted_hidden_water_body(self):
		self.update_water_body(is_active=0)
		frappe.delete_doc("Water Body", self.water_body_name)

		# Deleting a document deletes its Versions. The deletion is the only remaining
		# event, so it must be reported even if the Water Body was hidden before.
		events = self.get_events()
		self.assertEqual([event["event"] for event in events], ["Deleted"])
