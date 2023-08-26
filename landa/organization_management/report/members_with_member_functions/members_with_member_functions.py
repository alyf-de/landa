# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
from frappe import _

from landa.organization_management.birthday import (
	get_age,
	get_next_birthday,
	next_birthday_is_decadal,
)

COLUMNS = [
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
		"fieldname": "member_function_category",
		"fieldtype": "Data",
		"label": _("Member Function Categories"),
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
	{
		"fieldname": "full_address",
		"fieldtype": "Data",
		"label": _("Full Address"),
	},
	{
		"fieldname": "address_line1",
		"fieldtype": "Data",
		"label": _("Address Line 1"),
	},
	{"fieldname": "pincode", "fieldtype": "Data", "label": _("Pincode")},
	{"fieldname": "city", "fieldtype": "Data", "label": _("City")},
	{"fieldname": "award_list", "fieldtype": "Data", "label": _("Award List")},
	{
		"fieldname": "date_of_birth",
		"fieldtype": "Date",
		"label": _("Date of Birth"),
	},
	{"fieldname": "member_age", "fieldtype": "Data", "label": _("Age")},
	{
		"fieldname": "upcoming_birthday",
		"fieldtype": "Date",
		"label": _("Upcoming Birthday"),
	},
	{
		"fieldname": "is_decadal_birthday",
		"fieldtype": "Check",
		"label": _("Is Decadal Birthday"),
	},
]


def get_data(filters):
	def frappe_tuple_to_pandas_df(frappe_tuple, fields):
		df = pd.DataFrame(frappe_tuple, columns=fields)
		df.set_index("member", inplace=True)
		return df

	def remove_duplicate_indices(df, index="member", sort_by=None, keep="last"):
		"""Remove rows in dataframe with duplicate indeces.
		If sort_by is specified the dataframe is firsted sorted by these columns keeping the entry specified in keep, e.g. 'last'"""
		if sort_by is not None:
			df = df.sort_values(sort_by)
		return df.reset_index().drop_duplicates(subset=[index], keep=keep).set_index(index)

	def aggregate_entries(df, aggregate_field, groupby="member", sort_by=None):
		if sort_by is not None:
			df = df.sort_values(sort_by)
		aggregate_dict = {}
		for k in list(df):
			aggregate_dict[k] = "first"
		aggregate_dict[aggregate_field] = ", ".join
		df = df.groupby(groupby).agg(aggregate_dict)
		return df

	def get_contact_details(
		doctype: str, members: "list[str]", extra_fields: "list[str]"
	) -> "tuple[tuple]":
		return frappe.get_list(
			doctype,
			filters=[
				["Dynamic Link", "link_doctype", "=", "LANDA Member"],
				["Dynamic Link", "link_name", "in", members],
			],
			fields=extra_fields + ["`tabDynamic Link`.link_name as member"],
			as_list=True,
		)

	# load member functions from db
	member_function_fields = [
		"member",
		"member_function_category",
	]
	filters["status"] = "Active"
	member_functions = frappe.get_list(
		"Member Function",
		filters=filters,
		fields=member_function_fields,
	)
	MEMBERS = [m.member for m in member_functions]

	member_functions_df = pd.DataFrame.from_records(
		member_functions, columns=member_function_fields, index="member"
	)
	member_functions_df = aggregate_entries(member_functions_df, "member_function_category")

	reindex_df = member_functions_df

	# define the member master data that are supposed to be loaded
	member_fields = [
		"name as member",
		"first_name",
		"last_name",
		"date_of_birth",
		"organization",
		"organization_name",
	]
	members = frappe.get_list(
		"LANDA Member",
		fields=member_fields,
		filters={"name": ("in", MEMBERS)},
	)

	member_df = pd.DataFrame.from_records(
		members, columns=["member"] + member_fields[1:], index="member"
	)
	member_df["age"] = member_df["date_of_birth"].apply(get_age)
	member_df["upcoming_birthday"] = member_df["date_of_birth"].apply(get_next_birthday)
	member_df["is_decadal_birthday"] = member_df["age"].apply(next_birthday_is_decadal)

	# load awards from db
	award_fields = ["award_type", "issue_date", "member"]
	awards = frappe.get_list(
		"Award",
		fields=award_fields,
		filters={"member": ("in", MEMBERS)},
	)

	awards_df = pd.DataFrame.from_records(awards, columns=award_fields, index="member")
	awards_df["award_list"] = [
		at + " " + str(ad.year)
		for at, ad in zip(awards_df["award_type"].values, awards_df["issue_date"].values)
	]
	awards_df = aggregate_entries(awards_df, aggregate_field="award_list", sort_by=["issue_date"])
	awards_df.drop(award_fields[:-1], axis=1, inplace=True)

	# load addresses from db
	address_fields = ["address_line1", "pincode", "city"]
	addresses = get_contact_details("Address", MEMBERS, address_fields)

	# convert to pandas dataframe
	addresses_df = frappe_tuple_to_pandas_df(addresses, address_fields + ["member"])
	# remove all duplicate addresses by keeping only the last existing address
	addresses_df = remove_duplicate_indices(addresses_df)

	# merge all columns to one address column and add this as the first column
	addresses_df["full_address"] = (
		addresses_df["address_line1"] + ", " + addresses_df["pincode"] + " " + addresses_df["city"]
	)
	address_cols = addresses_df.columns.tolist()
	addresses_df = addresses_df[address_cols[-1:] + address_cols[:-1]]

	# load contacts from db that are linked to the member fucntions loaded before
	contact_fields = ["email_id", "phone", "mobile_no"]
	contacts = get_contact_details("Contact", MEMBERS, contact_fields)

	# convert to pandas dataframe
	contacts_df = frappe_tuple_to_pandas_df(contacts, contact_fields + ["member"])
	contacts_df = remove_duplicate_indices(contacts_df)

	# merge all dataframes from different doctypes and load data of all members without member functions only if necessary
	data = pd.concat(
		[member_df, member_functions_df, contacts_df, addresses_df, awards_df],
		axis=1,
	).reindex(reindex_df.index)
	# sort columns as needed
	data = data.reindex(
		[
			"first_name",
			"last_name",
			"organization",
			"organization_name",
			"member_function_category",
			"email_id",
			"phone",
			"mobile_no",
			"full_address",
			"address_line1",
			"pincode",
			"city",
			"award_list",
			"date_of_birth",
			"age",
			"upcoming_birthday",
			"is_decadal_birthday",
		],
		axis=1,
	)
	# replace NaNs with empty strings
	data.fillna("", inplace=True)

	# convert data back to tuple
	data.reset_index(inplace=True)
	data = tuple(data.itertuples(index=False, name=None))
	return data


def execute(filters):
	return COLUMNS, get_data(filters)
