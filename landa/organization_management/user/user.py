from frappe.core.doctype.user.user import User
from landa.utils import purge_all


def on_trash(user: User, event: str) -> None:
	purge_all("User", user.name)
