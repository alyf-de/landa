from timeit import default_timer as timer

import frappe
from frappe.utils import update_progress_bar

from landa.organization_management.address.address import autoname


def execute():
	doctype = "Address"
	all_addresses = frappe.get_all(doctype)
	total_addresses = len(all_addresses)
	last_duration = 0.0
	total_duration = 0.0

	for counter, address in enumerate(all_addresses):
		start_time = timer()
		avg_seconds = total_duration / (counter or 1)
		remaining_hours = round(
			avg_seconds * (total_addresses - counter) / 60 / 60, 2
		)
		update_progress_bar(
			f"Renaming Addresses ({round(avg_seconds)}s avg, {remaining_hours}h remaining)",
			counter,
			total_addresses,
		)
		doc = frappe.get_doc(doctype, address.name)

		old_name = address.name
		autoname(doc, None)	 # changes doc.name to the new name
		new_name = doc.name

		if new_name[-2:] == "-1":
			new_name = new_name[:-2]

		if old_name == new_name:
			continue

		try:
			frappe.rename_doc(
				doctype,
				old_name,
				new_name,
				ignore_permissions=True,  # checking permissions takes too long
				ignore_if_exists=True,	# don't rename if a record with the same name exists already
				show_alert=False,  # no need to show a UI alert, we're in the console
			)
		except frappe.exceptions.ValidationError:
			pass

		if counter > 0 and counter % 100 == 0:
			frappe.db.commit()

		end_time = timer()
		last_duration = end_time - start_time
		total_duration += last_duration
