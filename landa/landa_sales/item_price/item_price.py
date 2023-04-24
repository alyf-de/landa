def validate(item_price, event):
	"""
	Unset any values that might have been set by accident and will mess up pricing logic.

	For example, customer gets set automatically if it is set in session defaults. We need to unset it again.
	See https://github.com/frappe/frappe/issues/14290
	"""
	item_price.customer = ""
	item_price.supplier = ""
	item_price.uom = ""
	item_price.batch_no = ""
	item_price.lead_time_days = 0
