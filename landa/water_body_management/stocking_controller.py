from frappe.model.document import Document


class StockingController(Document):
	def validate(self):
		self.set_weight_per_size()
		self.set_quantity_per_size()
		self.set_total_price()

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

		self.price_for_total_weight = self.weight * self.price_per_kilogram
