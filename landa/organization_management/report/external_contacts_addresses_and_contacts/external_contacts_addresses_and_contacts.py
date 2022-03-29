# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import pandas as pd

import frappe


class Address(object):
	def __init__(self, filters):
		def add_key_from_filters(key, dict):
			if key in filters:
				dict[key] = filters[key]

		self.filter_external_contact = {}
		add_key_from_filters("organization", self.filter_external_contact)
		add_key_from_filters("is_magazine_recipient", self.filter_external_contact)

	def run(self):
		return self.get_columns(), self.get_data()

	def get_data(self):
		def frappe_tuple_to_pandas_df(frappe_tuple, fields):
			# convert to pandas dataframe
			df = pd.DataFrame(frappe_tuple, columns=fields)
			# set by external_contact ID as dataframe index
			df.set_index("external_contact", inplace=True)
			return df

		def remove_duplicate_indices(df, index="external_contact", sort_by=None, keep="last"):
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
				["Dynamic Link", "link_doctype", "=", "External Contact"],
				["Dynamic Link", "link_name", "in", [m[0] for m in frappe_tuple]],
			]

		# define the external_contact master data that are supposed to be loaded
		external_contact_fields = [
			"name",
			"first_name",
			"last_name",
			"organization",
			"is_magazine_recipient",
			# "organization_name",
		]
		external_contacts = frappe.db.get_list(
			"External Contact",
			filters=self.filter_external_contact,
			fields=external_contact_fields,
			as_list=True,
		)

		# convert to pandas dataframe
		external_contact_df = frappe_tuple_to_pandas_df(external_contacts, ["external_contact"] + external_contact_fields[1:])

		# define the labels of db entries that are supposed to be loaded
		link_field_label = "`tabDynamic Link`.link_name as external_contact"
		link_filters = get_link_filters(external_contacts)

		# load addresses from db
		address_fields = ["address_line1", "pincode", "city", "is_primary_address"]
		addresses = frappe.get_list(
			"Address",
			filters=link_filters,
			fields=address_fields + [link_field_label],
			as_list=True,
		)
		# convert to pandas dataframe
		addresses_df = frappe_tuple_to_pandas_df(addresses, address_fields + ["external_contact"])
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

		# load contacts from db that are linked to the member fucntions loaded before
		contact_fields = ["email_id", "phone", "mobile_no"]
		contacts = frappe.get_list("Contact", filters=link_filters, fields=contact_fields+[link_field_label], 
		as_list=True)
		# convert to pandas dataframe
		contacts_df=frappe_tuple_to_pandas_df(contacts,contact_fields+["external_contact"])
		contacts_df=remove_duplicate_indices(contacts_df)

		# merge all dataframes from different doctypes
		data = pd.concat([external_contact_df, addresses_df, contacts_df], axis=1).reindex(external_contact_df.index)
		# replace NaNs with empty strings
		data.fillna("", inplace=True)
		# convert data back to tuple
		data.reset_index(inplace=True)
		data = tuple(data.itertuples(index=False, name=None))
		return data

	def get_columns(self):
		return [
			{
				"fieldname": "external_contact",
				"fieldtype": "Link",
				"options": "External Contact",
				"label": "External Contact",
			},
			{"fieldname": "first_name", "fieldtype": "Data", "label": "First Name"},
			{"fieldname": "last_name", "fieldtype": "Data", "label": "Last Name"},
			{
				"fieldname": "organization",
				"fieldtype": "Link",
				"options": "Organization",
				"label": "Organization",
			},
			{"fieldname": "is_magazine_recipient", "fieldtype": "Check", "label": "Is Magazine Recipient"},
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
			"fieldname": "primary_email_address",
			"fieldtype": "Data",
			"label": "Primary Email Address"
			},
			{
			"fieldname": "primary_phone",
			"fieldtype": "Data",
			"label": "Primary Phone"
			},
			{
			"fieldname": "primary_mobile",
			"fieldtype": "Data",
			"label": "Primary Mobile"
			}
		]


def execute(filters=None):
	return Address(filters).run()
