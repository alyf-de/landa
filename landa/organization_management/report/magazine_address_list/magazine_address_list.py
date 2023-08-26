# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
import pandas as pd
from frappe import _


class Address:
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
			self.only_active_magazine = filters["only_active_magazine"]
		else:
			self.only_active_magazine = False

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
			"magazine_recipient",
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
		address_fields = ["address_line1", "pincode", "city"]
		addresses = frappe.get_list(
			"Address",
			filters=link_filters,
			fields=address_fields + [link_field_label],
			as_list=True,
		)
		# convert to pandas dataframe
		addresses_df = frappe_tuple_to_pandas_df(addresses, address_fields + ["member"])
		# remove all duplicate addresses by keeping only the last existing address
		addresses_df = remove_duplicate_indices(addresses_df)

		# merge all columns to one address column and add this as the first column
		addresses_df["full_address"] = (
			addresses_df["address_line1"] + ", " + addresses_df["pincode"] + " " + addresses_df["city"]
		)

		# load addresses from db
		permit_fields = ["year", "member", "docstatus"]
		permits = frappe.get_list(
			"Yearly Fishing Permit",
			filters=[["Yearly Fishing Permit", "member", "in", get_member_filter(members)]],
			fields=permit_fields,
			as_list=True,
		)
		# convert to pandas dataframe
		permits_df = frappe_tuple_to_pandas_df(permits, permit_fields)
		permits_df = permits_df[permits_df["docstatus"] == 1]
		# remove column 'status'
		permits_df.drop("docstatus", axis=1, inplace=True)
		permits_df = remove_duplicate_indices(permits_df, sort_by="year")

		this_year = int(datetime.today().strftime("%Y"))
		this_month = int(datetime.today().strftime("%m"))
		# if this month is January to June: members need a permit for this year or last year:
		if this_month < 7:
			permits_df["permit_active"] = [
				int((this_year - int(y)) <= 1) for y in permits_df["year"].values
			]
		# if this month is July to December: members need a permit for this year:
		else:
			permits_df["permit_active"] = [int(this_year == int(y)) for y in permits_df["year"].values]
		# merge all dataframes from different doctypes
		data = pd.concat([member_df, permits_df, addresses_df], axis=1).reindex(member_df.index)
		data["magazine_active"] = data["permit_active"] * data["magazine_recipient"]
		if self.only_active_magazine:
			data = data[data["magazine_active"] == 1]
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
				"fieldname": "magazine_recipient",
				"fieldtype": "Check",
				"label": _("Is Magazine Recipient"),
			},
			{
				"fieldname": "year",
				"fieldtype": "Int",
				"label": _("Year"),
			},
			{
				"fieldname": "permit_active",
				"fieldtype": "Check",
				"label": _("Permit Is Active"),
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
			{
				"fieldname": "magazine_active",
				"fieldtype": "Check",
				"label": _("Magazine Is Active"),
			},
		]


def execute(filters=None):
	return Address(filters).run()
