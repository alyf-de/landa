from frappe.utils.nestedset import rebuild_tree

from landa.print_format_sources.print_formats import sync_print_formats


def after_migrate(*args, **kwargs):
	# Make sure Organization tree is still valid after migration
	rebuild_tree("Organization", "parent_organization")
	sync_print_formats()
