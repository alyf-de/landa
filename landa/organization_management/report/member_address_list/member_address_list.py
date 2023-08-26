# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
from frappe import _

from ..member.member import Member, get_link_filters, remove_duplicate_indices


class Address(Member):
	def __init__(self, filters):
		super().__init__(filters)

	def get_data(self):
		self.set_members()

		# define the labels of db entries that are supposed to be loaded
		link_field_label = "`tabDynamic Link`.link_name as member"
		link_filters = get_link_filters(self.members)

		# load addresses from db
		address_fields = ["address_line1", "pincode", "city"]
		addresses = frappe.get_list(
			"Address",
			filters=link_filters,
			fields=address_fields + [link_field_label],
			as_list=True,
		)
		# convert to pandas dataframe
		addresses_df = pd.DataFrame(addresses, columns=address_fields + ["member"])
		addresses_df.set_index("member", inplace=True)

		# remove all duplicate addresses by keeping only the last existing address
		addresses_df = remove_duplicate_indices(addresses_df)

		# merge all columns to one address column and add this as the first column
		addresses_df["full_address"] = (
			addresses_df["address_line1"] + ", " + addresses_df["pincode"] + " " + addresses_df["city"]
		)

		# merge all dataframes from different doctypes
		data = pd.concat([self.members_df, addresses_df], axis=1).reindex(self.members_df.index)

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
				"fieldname": "address_line1",
				"fieldtype": "Data",
				"label": _("Address Line 1"),
			},
			{"fieldname": "pincode", "fieldtype": "Data", "label": _("Pincode")},
			{"fieldname": "city", "fieldtype": "Data", "label": _("City")},
			{
				"fieldname": "full_address",
				"fieldtype": "Data",
				"label": _("Full Address"),
			},
		]


def execute(filters=None):
	return Address(filters).run()
