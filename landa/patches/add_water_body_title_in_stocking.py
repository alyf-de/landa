import frappe


def execute():
	frappe.db.sql(
		"""
		UPDATE `tabStocking Target` AS st
		INNER JOIN `tabWater Body` AS wb ON wb.name = st.water_body
		SET st.water_body_title = wb.title
	"""
	)

	frappe.db.sql(
		"""
		UPDATE `tabStocking Measure` AS sm
		INNER JOIN `tabWater Body` AS wb ON wb.name = sm.water_body
		SET sm.water_body_title = wb.title
	"""
	)
