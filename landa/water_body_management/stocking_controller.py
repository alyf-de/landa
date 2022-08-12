import frappe
from frappe import _
from frappe.model.document import Document

from landa.utils import get_current_member_data


class StockingController(Document):
	def validate(self):
		self.validate_own_regional_organization()
		self.validate_own_water_body()
		self.set_weight_per_size()
		self.set_quantity_per_size()
		self.set_total_price()

	def validate_own_regional_organization(self):
		member_data = get_current_member_data()
		if member_data and member_data.regional_organization != self.organization:
			frappe.throw(_("Please select your own regional Organization."))

	def validate_own_water_body(self):
		if (
			self.water_body
			and frappe.db.get_value("Water Body", self.water_body, "organization")
			!= self.organization
		):
			frappe.throw(
				_("Please select a Water Body from your own regional Organization.")
			)

	def set_weight_per_size(self):
		if not (self.weight and self.water_body_size):
			return

		self.weight_per_water_body_size = self.weight / self.water_body_size
		self.unit_of_weight_per_water_body_size = f"Kg / {self.water_body_size_unit}"

	def set_quantity_per_size(self):
		if not (self.quantity and self.water_body_size):
			return

		self.quantity_per_water_body_size = self.weight / self.water_body_size
		self.unit_of_quantity_per_water_body_size = f"Stk / {self.water_body_size_unit}"

	def set_total_price(self):
		if not (self.weight and self.price_per_kilogram):
			self.price_for_total_weight = 0
		else:
			self.price_for_total_weight = self.weight * self.price_per_kilogram
