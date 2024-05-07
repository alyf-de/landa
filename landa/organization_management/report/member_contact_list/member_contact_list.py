# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
from frappe import _

from ..member.member import Member, get_link_filters, remove_duplicate_indices


class Contact(Member):
	def __init__(self, filters):
		super().__init__(filters)

	def get_data(self):
		self.set_members()

		# define the labels of db entries that are supposed to be loaded
		link_field_label = "`tabDynamic Link`.link_name as member"
		link_filters = get_link_filters(self.members)

		# load contacts from db that are linked to the member fucntions loaded before
		contact_fields = ["email_id", "phone", "mobile_no"]
		contacts = frappe.get_list(
			"Contact",
			filters=link_filters,
			fields=contact_fields + [link_field_label],
			as_list=True,
		)

		# convert to pandas dataframe
		contacts_df = pd.DataFrame(contacts, columns=contact_fields + ["member"])
		contacts_df.set_index("member", inplace=True)
		contacts_df = remove_duplicate_indices(contacts_df)

		# merge all dataframes from different doctypes
		data = pd.concat([self.members_df, contacts_df], axis=1).reindex(self.members_df.index)

		data.fillna("", inplace=True)

		# convert data back to tuple
		data.reset_index(inplace=True)
		data = tuple(data.itertuples(index=False, name=None))

		return data

	def get_columns(self):
		return [
			{
				"fieldname": "landa_member",
				"fieldtype": "Link",
				"options": "LANDA Member",
				"label": _("Member"),
			},
			{"fieldname": "first_name", "fieldtype": "Data", "label": _("First Name")},
			{"fieldname": "last_name", "fieldtype": "Data", "label": _("Last Name")},
			{
				"fieldname": "organization",
				"fieldtype": "Link",
				"options": "Organization",
				"label": _("Organization"),
			},
			{
				"fieldname": "organization_name",
				"fieldtype": "Data",
				"label": _("Organization Name"),
			},
			{
				"fieldname": "primary_email_address",
				"fieldtype": "Data",
				"label": _("Primary Email Address"),
			},
			{
				"fieldname": "primary_phone",
				"fieldtype": "Data",
				"label": _("Primary Phone"),
			},
			{
				"fieldname": "primary_mobile",
				"fieldtype": "Data",
				"label": _("Primary Mobile"),
			},
		]


def execute(filters=None):
	return Contact(filters).run()
