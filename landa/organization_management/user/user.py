from frappe.core.doctype.user.user import User
from landa.utils import remove_from_table, db_unset


def on_trash(user: User, event: str) -> None:
	db_unset("LANDA Member", "user", user.name)
	remove_from_table("Note", "seen_by", {"user": user.name})
