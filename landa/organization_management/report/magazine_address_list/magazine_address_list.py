# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import pandas as pd

import frappe

from datetime import datetime


class Address(object):
	def __init__(self, filters):
		# set filters
		self.filter_name = {}

		def add_key_from_filters(key, dict):
			if key in filters:
				dict[key] = filters[key]

		for n in ["first_name", "last_name"]:
			add_key_from_filters(n, self.filter_name)

		self.filter_member = self.filter_name.copy()
		add_key_from_filters("organization", self.filter_member)

		if "only_active_magazine" in filters:
			self.only_active_magazine=filters["only_active_magazine"]
		else:
			self.only_active_magazine=False

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

		def get_member_filter(frappe_tuple):
			return [m[0] for m in frappe_tuple]

		# define the member master data that are supposed to be loaded
		member_fields = [
			"name",
			"first_name",
			"last_name",
			"organization",
			"organization_name",
			"magazine_recipient"
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

		# load addresses from db
		address_fields = ["address_line1", "pincode", "city", "is_primary_address"]
		addresses = frappe.get_list(
			"Address",
			filters=link_filters,
			fields=address_fields + [link_field_label],
			as_list=True,
		)
		# convert to pandas dataframe
		addresses_df = frappe_tuple_to_pandas_df(addresses, address_fields + ["member"])
		# remove all duplicate addresses by keeping only the primary address or last existing address if there is no primary address
		addresses_df = remove_duplicate_indices(
			addresses_df, sort_by="is_primary_address"
		)

		# merge all columns to one address column and add this as the first column
		addresses_df["full_address"] = (
			addresses_df["address_line1"]
			+ ", "
			+ addresses_df["pincode"]
			+ " "
			+ addresses_df["city"]
		)

		# remove column 'is_primary_address'
		addresses_df.drop("is_primary_address", axis=1, inplace=True)

		# load addresses from db
		permit_fields = ["year","member","docstatus"]
		permits = frappe.get_list(
			"Yearly Fishing Permit",
			filters=[['Yearly Fishing Permit', 'member', 'in', get_member_filter(members)]],
			fields=permit_fields,
			as_list=True,
		)
		# convert to pandas dataframe
		permits_df = frappe_tuple_to_pandas_df(permits, permit_fields)
		permits_df=permits_df[permits_df['docstatus']==1]
		# remove column 'status'
		permits_df.drop("docstatus", axis=1, inplace=True)
		permits_df = remove_duplicate_indices(
			permits_df, sort_by="year"
		)

		
		this_year=int(datetime.today().strftime('%Y'))
		this_month=int(datetime.today().strftime('%m'))
		# if this month is January to June: members need a permit for this year or last year:
		if this_month<7:
			permits_df["permit_active"]=[int((this_year-int(y))<=1) for y in permits_df["year"].values]
		# if this month is July to December: members need a permit for this year:
		else:
			permits_df["permit_active"]=[int(this_year==int(y)) for y in permits_df["year"].values]
		# merge all dataframes from different doctypes
		data = pd.concat([member_df, permits_df, addresses_df], axis=1).reindex(member_df.index)
		data["magazine_active"]=data["permit_active"]*data["magazine_recipient"]
		if self.only_active_magazine:
			data=data[data["magazine_active"]==1]
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
				"fieldname": "magazine_recipient",
				"fieldtype": "Check",
				"label": "Is Magazine Recipient",
			},
			{
				"fieldname": "year",
				"fieldtype": "Int",
				"label": "Year",
			},
			{
				"fieldname": "permit_active",
				"fieldtype": "Check",
				"label": "Permit Is Active",
			},
			{
				"fieldname": "address_line1",
				"fieldtype": "Data",
				"label": "Address Line 1",
			},
			{"fieldname": "pincode", "fieldtype": "Data", "label": "Pincode"},
			{"fieldname": "city", "fieldtype": "Data", "label": "City"},
			{
				"fieldname": "full_address",
				"fieldtype": "Data",
				"label": "Primary Address (Full)",
			},
			{
				"fieldname": "magazine_active",
				"fieldtype": "Check",
				"label": "Magazine Is Active",
			}
		]


def execute(filters=None):
	return Address(filters).run()
