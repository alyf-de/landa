"""Fix Redis type mismatch issue after switching from hash to key-value storage."""

import frappe

from landa.water_body_management.doctype.water_body.water_body import rebuild_water_body_cache


def execute():
	# Get the Redis client
	redis_client = frappe.cache()

	# Delete the old hash-type keys if they exist
	keys_to_fix = [
		"water_body_data",
		"fish_species_data",
		"water_body_data_in_progress",
	]

	for key in keys_to_fix:
		# Try both with and without the prefix, since old keys might not have used make_key
		keys_to_try = [
			key,  # Raw key without prefix
			redis_client.make_key(key),  # Key with prefix
		]

		for full_key in keys_to_try:
			try:
				# Try to delete the key regardless of its type
				if redis_client.exists(full_key):
					redis_client.delete(full_key)
					frappe.log_error(title="Redis Type Fix", message=f"Deleted Redis key: {full_key}")
			except Exception:
				# Silently continue - key might not exist or already be deleted
				pass

	# Now rebuild the caches with the correct type
	rebuild_water_body_cache()
