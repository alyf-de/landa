# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import numpy as np
import pandas as pd


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
			"has_special_yearly_fishing_permit_1",
			"has_special_yearly_fishing_permit_2",
			"youth_membership",
			"additional_information",
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
				"label": "Member ID",
				"fieldtype": "Link",
				"fieldname": "name",
				"options": "LANDA Member",
			},
			{
				"label": "Last Name",
				"fieldtype": "Data",
				"fieldname": "last_name",
			},
			{
				"label": "First Name",
				"fieldtype": "Data",
				"fieldname": "first_name",
			},
			{
				"label": "Date of Birth",
				"fieldtype": "Date",
				"fieldname": "date_of_birth",
			},
			{
				"label": "Address ID",
				"fieldtype": "Link",
				"fieldname": "address_name",
				"options": "Address",
			},
			{
				"label": "Address Line 1",
				"fieldtype": "Data",
				"fieldname": "address_line1",
			},
			{
				"label": "Pincode",
				"fieldtype": "Data",
				"fieldname": "pincode",
			},
			{
				"label": "City",
				"fieldtype": "Data",
				"fieldname": "city",
			},
			{
				"label": "Is Supporting Member",
				"fieldtype": "Check",
				"fieldname": "is_supporting_member",
			},
			{
				"label": "Has Key",
				"fieldtype": "Check",
				"fieldname": "has_key",
			},
			{
				"label": "Organization",
				"fieldtype": "Link",
				"fieldname": "organization",
				"options": "Organization",
			},
			{
				"label": "ID Yearly Fishing Permit",
				"fieldtype": "Link",
				"fieldname": "yearly_fishing_permit",
				"options": "Yearly Fishing Permit",
			},
			{
				"label": "Year of Yearly Fishing Permit",
				"fieldtype": "Data",
				"fieldname": "year",
			},
			{
				"label": "Yearly Fishing Permit Type",
				"fieldtype": "Link",
				"fieldname": "type",
				"options": "Yearly Fishing Permit Type",
			},
			{
				"label": "Issue Date of Yearly Fishing Permit",
				"fieldtype": "Date",
				"fieldname": "date_of_issue",
			},
			{
				"label": "Yearly Fishing Permit Number",
				"fieldtype": "Data",
				"fieldname": "number",
			},
			{
				"label": "Hat Sachsen-Anhalt Erlaubnisschein",
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_1",
			},
			{
				"label": "Hat Brandenburg Erlaubnisschein",
				"fieldtype": "Check",
				"fieldname": "has_special_yearly_fishing_permit_2",
			},
			{
				"label": "Youth Membership",
				"fieldtype": "Check",
				"fieldname": "youth_membership",
			},
			{
				"label": "Additional Information",
				"fieldtype": "Data",
				"fieldname": "additional_information",
			},
		]


def execute(filters=None):
	return LANDACurrentMemberData(filters).run()
