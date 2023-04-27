import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests.utils import FrappeTestCase

from landa.water_body_management.report.catch_log_statistics.catch_log_statistics import get_data

test_dependencies = ["Catch Log Entry"]


class TestCatchLogStatistics(FrappeTestCase):
	def test_catch_log_statistics(self):
		water_body = "A01-001"
		fish_species = "Barsch"
		amount = 5
		weight_in_kg = 12

		frappe.db.delete("Catch Log Entry")
		create_cle(fish_species, amount, weight_in_kg)

		data = get_data(
			{
				"from_year": "2020",
				"to_year": "2023",
				"water_body": water_body,
			}
		)
		row = data[0]
		self.assertEqual(row[0], water_body)
		self.assertEqual(row[1], fish_species)
		self.assertEqual(row[2], amount)
		self.assertEqual(row[3], weight_in_kg)
		self.assertEqual(row[4], 0)

		create_cle(fish_species, amount, weight_in_kg)

		data = get_data(
			{
				"from_year": "2020",
				"to_year": "2023",
				"water_body": water_body,
				"fish_species": fish_species,
			}
		)
		row = data[0]
		self.assertEqual(row[0], water_body)
		self.assertEqual(row[1], fish_species)
		self.assertEqual(row[2], amount * 2)
		self.assertEqual(row[3], weight_in_kg * 2)
		self.assertEqual(row[4], 0)


def create_cle(fish_species, amount, weight_in_kg):
	cle = frappe.get_doc(
		{
			"doctype": "Catch Log Entry",
			"water_body": "A01-001",
			"year": 2023,
			"fishing_days": 8,
			"organization": "REG-001",
			"origin_of_catch_log_entry": "Verein",
			"workflow_state": "In Progress",
			"fish_catches": [
				{"fish_species": fish_species, "amount": amount, "weight_in_kg": weight_in_kg}
			],
		}
	)
	cle.save()
	apply_workflow(cle, "File this record")
	apply_workflow(cle, "Approve")
