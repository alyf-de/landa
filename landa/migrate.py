from frappe.utils.nestedset import rebuild_tree


def after_migrate(*args, **kwargs):
	# Make sure Organization tree is still valid after migration
	rebuild_tree("Organization", "parent_organization")
