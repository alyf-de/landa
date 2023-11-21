# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import numpy as np
import pandas as pd
from frappe import _


class LANDACurrentMemberData:
	def __init__(self, filters):
		# set attribute to load only members and remove it from filters
		self.filter = filters  # .pop('organization', None)

	def run(self):
		return self.get_columns(), self.get_data()

	def get_data(self):
		def frappe_tuple_to_pandas_df(frappe_tuple, fields):
			# convert to pandas dataframe
			df = pd.DataFrame(frappe_tuple, columns=fields)
			# set by member ID as dataframe index
			df.set_index("member", inplace=True)
			return df

		def remove_duplicate_indices(df, index="member", sort_by=None, keep="last"):
			"""Remove rows in dataframe with duplicate indeces.
			If sort_by is specified the dataframe is firsted sorted by these columns keeping the entry specified in keep, e.g. 'last'"""
			if sort_by is not None:
				df = df.sort_values(sort_by)
			return df.reset_index().drop_duplicates(subset=[index], keep=keep).set_index(index)

		def get_link_filters(frappe_tuple):
			member_ids = [m[0] for m in frappe_tuple]  # list of member names (ID)
			link_filters = [
				["Dynamic Link", "link_doctype", "=", "LANDA Member"],
				["Dynamic Link", "link_name", "in", member_ids],
			]
			return member_ids, link_filters

		# define the member master data that are supposed to be loaded
		member_fields = [
			"name",
			"last_name",
			"first_name",
			"date_of_birth",
			"organization",
			"is_supporting_member",
			"has_key",
			"youth_membership",
			"additional_information",
			"has_special_yearly_fishing_permit_1",
			"has_special_yearly_fishing_permit_2",
			"has_special_yearly_fishing_permit_3",
			"has_special_yearly_fishing_permit_4",
			"has_special_yearly_fishing_permit_5",
			"has_special_yearly_fishing_permit_6",
			"has_special_yearly_fishing_permit_7",
		]
		members = frappe.db.get_list(
			"LANDA Member", filters=self.filter, fields=member_fields, as_list=True
		)
		# convert to pandas dataframe
		member_df = frappe_tuple_to_pandas_df(members, ["member"] + member_fields[1:])
		# create empty clomuns for yearly fishing permit
		fishing_permit_columns = [
			"name",
			"member",
			"year",
			"type",
			"date_of_issue",
			"number",
		]
		fishing_permits = frappe.get_list(
			"Yearly Fishing Permit", fields=fishing_permit_columns, as_list=True
		)
		# convert to pandas dataframe
		fishing_permits_df = frappe_tuple_to_pandas_df(fishing_permits, fishing_permit_columns)
		fishing_permits_df.rename({"name": "yearly_fishing_permit"}, axis=1, inplace=True)
		fishing_permits_df = remove_duplicate_indices(
			fishing_permits_df, sort_by=["year", "date_of_issue"]
		)

		# define the labels of db entries that are supposed to be loaded
		link_field_label = "`tabDynamic Link`.link_name as member"
		member_ids, link_filters = get_link_filters(members)
		# load addresses from db
		address_fields = ["name", "address_line1", "pincode", "city"]
		addresses = frappe.get_list(
			"Address",
			filters=link_filters,
			fields=address_fields + [link_field_label],
			as_list=True,
		)
		# convert to pandas dataframe
		addresses_df = frappe_tuple_to_pandas_df(addresses, address_fields + ["member"])
		# rename index column
		addresses_df.rename({"name": "address_name"}, axis=1, inplace=True)

		# merge members and addresses from different doctypes
		data = pd.concat([member_df, fishing_permits_df], axis=1).reindex(member_df.index)
		data = pd.merge(data, addresses_df, on="member", how="outer")

		# sort dataframe like report columns
		sorted_columns = [c["fieldname"] for c in self.get_columns()][1:]
		data = data[sorted_columns]
		# replace NaNs with empty strings
		data.fillna("", inplace=True)
		# convert data back to tuple
		data.reset_index(inplace=True)
		data = tuple(data.itertuples(index=False, name=None))
		return data

	def get_columns(self):
		return [
			{
				"label": _("Member ID"),
				"fieldtype": "Link",
				"fieldname": "name",
				"options": "LANDA Member",
			},
			{
				"label": _("Last Name"),
				"fieldtype": "Data",
				"fieldname": "last_name",
			},
			{
				"label": _("First Name"),
				"fieldtype": "Data",
				"fieldname": "first_name",
			},
			{
				"label": _("Date of Birth"),
				"fieldtype": "Date",
				"fieldname": "date_of_birth",
			},
			{
				"label": _("Address ID"),
				"fieldtype": "Link",
				"fieldname": "address_name",
				"options": "Address",
			},
			{
				"label": _("Address Line 1"),
				"fieldtype": "Data",
				"fieldname": "address_line1",
			},
			{
				"label": _("Pincode"),
				"fieldtype": "Data",
				"fieldname": "pincode",
			},
			{
				"label": _("City"),
				"fieldtype": "Data",
				"fieldname": "city",
			},
			{
				"label": _("Is Supporting Member"),
				"fieldtype": "Check",
				"fieldname": "is_supporting_member",
			},
			{
				"label": _("Has Key"),
				"fieldtype": "Check",
				"fieldname": "has_key",
			},
			{
				"label": _("Youth Membership"),
				"fieldtype": "Check",
				"fieldname": "youth_membership",
			},
			{
				"label": _("Additional Information"),
				"fieldtype": "Data",
				"fieldname": "additional_information",
			},
			{
				"label": _("Organization"),
				"fieldtype": "Link",
				"fieldname": "organization",
				"options": "Organization",
			},
			{
				"label": _("ID Yearly Fishing Permit"),
				"fieldtype": "Link",
				"fieldname": "yearly_fishing_permit",
				"options": "Yearly Fishing Permit",
			},
			{
				"label": _("Year of Yearly Fishing Permit"),
				"fieldtype": "Data",
				"fieldname": "year",
			},
			{
				"label": _("Yearly Fishing Permit Type"),
				"fieldtype": "Link",
				"fieldname": "type",
				"options": "Yearly Fishing Permit Type",
			},
			{
				"label": _("Issue Date of Yearly Fishing Permit"),
				"fieldtype": "Date",
				"fieldname": "date_of_issue",
			},
			{
				"label": _("Yearly Fishing Permit Number"),
				"fieldtype": "Data",
				"fieldname": "number",
			},
			{
				"label": _("ES Sachsen-Anhalt"),
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_1",
			},
			{
				"label": _("ES Brandenburg"),
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_2",
			},
			{
				"label": _("ES Berlin"),
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_3",
			},
			{
				"label": _("ES Mecklenburg-Vorpommern"),
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_4",
			},
			{
				"label": _("ES Saalekaskade"),
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_5",
			},
			{
				"label": _("ES LAVT"),
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_6",
			},
			{
				"label": _("ES VANT"),
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_7",
			},
		]


def execute(filters=None):
	return LANDACurrentMemberData(filters).run()
