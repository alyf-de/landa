import frappe
from frappe import _


@frappe.whitelist()
def get_member_functions_html(organization: str) -> str:
	member_functions = frappe.get_list(
		"Member Function",
		filters={"organization": organization, "status": "Active"},
		fields=[
			"name",
			"member_function_category",
			"member",
			"member_first_name",
			"member_last_name",
			"start_date",
		],
		order_by="member_function_category asc",
	)

	if not member_functions:
		empty_message = _("No active member functions.")
		return f"<p>{empty_message}</p>"

	function_label = _("Function")
	member_label = _("Member")
	since_label = _("Since")

	rows = ""
	for mf in member_functions:
		start_date = frappe.format(mf.start_date, {"fieldtype": "Date"})
		rows += f"""<tr>
			<td><a href="/app/member-function/{mf.name}">{mf.member_function_category}</a></td>
			<td><a href="/app/landa-member/{mf.member}">{mf.member_first_name} {mf.member_last_name}</a></td>
			<td>{start_date}</td>
		</tr>"""

	return f"""
	<table class="table table-bordered table-sm" style="margin-bottom: 20px">
		<thead>
			<tr>
				<th>{function_label}</th>
				<th>{member_label}</th>
				<th>{since_label}</th>
			</tr>
		</thead>
		<tbody>
			{rows}
		</tbody>
	</table>"""
