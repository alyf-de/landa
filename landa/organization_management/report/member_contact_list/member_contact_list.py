# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import pandas as pd

import frappe


class Contact(object):
	def __init__(self, filters):
		def add_key_from_filters(key, filterlist):
			if key in filters:
				filterlist.append([key, "like", "%" + filters[key] + "%"])

		# set filters
		self.filter_member = []

		for n in ["name", "first_name", "last_name", "organization"]:
			add_key_from_filters(n, self.filter_member)

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

			return (
				df.reset_index()
				.drop_duplicates(subset=[index], keep=keep)
				.set_index(index)
			)

		def get_link_filters(frappe_tuple):
			return [
				["Dynamic Link", "link_doctype", "=", "LANDA Member"],
				["Dynamic Link", "link_name", "in", [m[0] for m in frappe_tuple]],
			]

		# define the member master data that are supposed to be loaded
		member_fields = [
			"name",
			"first_name",
			"last_name",
			"organization",
			"organization_name",
		]
		members = frappe.db.get_list(
			"LANDA Member",
			filters=self.filter_member,
			fields=member_fields,
			as_list=True,
		)

		# convert to pandas dataframe
		member_df = frappe_tuple_to_pandas_df(members, ["member"] + member_fields[1:])

		# define the labels of db entries that are supposed to be loaded
		link_field_label = "`tabDynamic Link`.link_name as member"
		link_filters = get_link_filters(members)

		# load contacts from db that are linked to the member fucntions loaded before
		contact_fields = ["email_id", "phone", "mobile_no"]
		contacts = frappe.get_list(
			"Contact",
			filters=link_filters,
			fields=contact_fields + [link_field_label],
			as_list=True,
		)
		# convert to pandas dataframe
		contacts_df = frappe_tuple_to_pandas_df(contacts, contact_fields + ["member"])
		contacts_df = remove_duplicate_indices(contacts_df)

		# merge all dataframes from different doctypes
		data = pd.concat([member_df, contacts_df], axis=1).reindex(member_df.index)
		# replace NaNs with empty strings
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
				"label": "Member",
			},
			{"fieldname": "first_name", "fieldtype": "Data", "label": "First Name"},
			{"fieldname": "last_name", "fieldtype": "Data", "label": "Last Name"},
			{
				"fieldname": "organization",
				"fieldtype": "Link",
				"options": "Organization",
				"label": "Organization",
			},
			{
				"fieldname": "organization_name",
				"fieldtype": "Data",
				"label": "Organization Name",
			},
			{
				"fieldname": "primary_email_address",
				"fieldtype": "Data",
				"label": "Primary Email Address",
			},
			{
				"fieldname": "primary_phone",
				"fieldtype": "Data",
				"label": "Primary Phone",
			},
			{
				"fieldname": "primary_mobile",
				"fieldtype": "Data",
				"label": "Primary Mobile",
			},
		]


def execute(filters=None):
	return Contact(filters).run()
