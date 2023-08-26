# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

from typing import List

import frappe
import pandas as pd
from frappe import _

COLUMNS = [
	{
		"fieldname": "external_contact",
		"fieldtype": "Link",
		"options": "External Contact",
		"label": _("External Contact"),
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
		"fieldname": "is_magazine_recipient",
		"fieldtype": "Check",
		"label": _("Is Magazine Recipient"),
	},
	{
		"fieldname": "external_functions",
		"fieldtype": "Data",
		"label": _("External Functions"),
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


def get_data(filters):
	def to_df(records, columns):
		"""Convert a list of records to a dataframe."""
		index = "external_contact"
		return pd.DataFrame.from_records(records, columns=[index] + columns, index=index)

	def remove_duplicate_indices(df, index="external_contact", sort_by=None, keep="last"):
		"""Remove rows in dataframe with duplicate indeces.
		If sort_by is specified the dataframe is firsted sorted by these columns keeping the entry specified in keep, e.g. 'last'"""
		if sort_by is not None:
			df = df.sort_values(sort_by)

		return df.reset_index().drop_duplicates(subset=[index], keep=keep).set_index(index)

	def get_link_filters(link_names: List[str]):
		return [
			["Dynamic Link", "link_doctype", "=", "External Contact"],
			["Dynamic Link", "link_name", "in", link_names],
		]

	# define the external_contact master data that are supposed to be loaded
	external_contact_fields = [
		"first_name",
		"last_name",
		"organization",
		"is_magazine_recipient",
	]
	external_contacts = frappe.db.get_list(
		"External Contact",
		filters=filters,
		fields=["name as external_contact"] + external_contact_fields,
	)

	# convert to pandas dataframe
	external_contact_df = to_df(external_contacts, external_contact_fields)
	external_contact_ids = tuple(external_contact_df.index.values)

	# define the labels of db entries that are supposed to be loaded
	link_field = "`tabDynamic Link`.link_name as external_contact"
	link_filters = get_link_filters(external_contact_ids)

	# load addresses from db
	address_fields = ["address_line1", "pincode", "city"]
	addresses = frappe.get_list(
		"Address",
		filters=link_filters,
		fields=[link_field] + address_fields,
	)
	# convert to pandas dataframe
	addresses_df = to_df(addresses, address_fields)
	# remove all duplicate addresses by keeping only the last existing address
	addresses_df = remove_duplicate_indices(addresses_df)

	# merge all columns to one address column and add this as the first column
	addresses_df["full_address"] = (
		addresses_df["address_line1"] + ", " + addresses_df["pincode"] + " " + addresses_df["city"]
	)

	# load contacts from db that are linked to the member fucntions loaded before
	contact_fields = ["email_id", "phone", "mobile_no"]
	contacts = frappe.get_list(
		"Contact",
		filters=link_filters,
		fields=[link_field] + contact_fields,
	)
	# convert to pandas dataframe
	contacts_df = to_df(contacts, contact_fields)
	contacts_df = remove_duplicate_indices(contacts_df)

	external_functions = frappe.get_list(
		"External Contact Function",
		filters={
			"parenttype": "External Contact",
			"parent": ("in", external_contact_ids),
		},
		fields=["parent as external_contact", "external_function"],
	)
	external_functions_df = to_df(external_functions, ["external_function"])
	external_functions_df = pd.DataFrame(
		external_functions_df.groupby("external_contact")["external_function"].apply(
			lambda functions: ", ".join(functions.astype(str))
		),
	)

	# merge all dataframes from different doctypes
	data = pd.concat([external_contact_df, external_functions_df, addresses_df, contacts_df], axis=1)
	# replace NaNs with empty strings
	data.fillna("", inplace=True)
	# convert data back to tuple
	return tuple(data.itertuples(index=True, name=None))


def execute(filters=None):
	return COLUMNS, get_data(filters)
