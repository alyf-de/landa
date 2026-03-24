# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
import pandas as pd
from frappe import _


def execute(filters=None):
	organization = filters.pop("organization", None)
	if not organization:
		frappe.throw(_("Organization is required"))

	return get_columns(), get_data(organization)

<<<<<<< HEAD
	def get_data(self):
		def frappe_tuple_to_pandas_df(frappe_tuple, fields):
			# convert to pandas dataframe
			df = pd.DataFrame(frappe_tuple, columns=fields)
			# set by member ID as dataframe index
			df.set_index("member", inplace=True)
			return df
=======
>>>>>>> 1f8e062 (perf(Current Member Data): make organization filter mandatory, filter yearly fishing permits (LAN-895) (#318))

def get_data(organization: str):
	"""Assemble rows for the current-member report from several DocTypes.

	Loads LANDA Member master data (respecting the organization filter), Yearly
	Fishing Permit rows keyed by member (keeping one row per member after
	sorting by year), and Address rows dynamically linked to those members.
	The frames are merged and ordered to match `get_columns()`, then
	returned as tuples with empty strings instead of missing values.

	Permissions: every fetch goes through Frappe `get_list`, so the result only
	contains documents and fields the current user is allowed to read.
	"""
	members = frappe.get_list(
		"LANDA Member",
		filters={"organization": organization},
		fields=[
			"name as member",
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
<<<<<<< HEAD
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
		]
		fishing_permits = frappe.get_list(
			"Yearly Fishing Permit", fields=fishing_permit_columns, as_list=True
		)
		# convert to pandas dataframe
		fishing_permits_df = frappe_tuple_to_pandas_df(fishing_permits, fishing_permit_columns)
		fishing_permits_df.rename({"name": "yearly_fishing_permit"}, axis=1, inplace=True)
		fishing_permits_df = remove_duplicate_indices(fishing_permits_df, sort_by=["year"])

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
=======
		],
	)
	if not members:
		return ()

	member_df = pd.DataFrame.from_records(members, index="member")
	this_year = datetime.now().year
	fishing_permits = frappe.get_list(
		"Yearly Fishing Permit",
		filters={
			"organization": organization,
			"docstatus": 1,
			"year": ["in", [this_year - 1, this_year, this_year + 1]],
		},
		fields=[
			"name as yearly_fishing_permit",
			"member",
			"year",
			"type",
		],
	)
	fishing_permits_df = pd.DataFrame.from_records(fishing_permits, index="member")
	# Remove rows in dataframe with duplicate indeces.
	# The dataframe is firsted sorted by year keeping the 'last' entry.
	fishing_permits_df = fishing_permits_df.sort_values(["year"])
	fishing_permits_df = (
		fishing_permits_df.reset_index().drop_duplicates(subset=["member"], keep="last").set_index("member")
	)

	# load addresses from db
	addresses = frappe.get_list(
		"Address",
		filters=[
			["Dynamic Link", "link_doctype", "=", "LANDA Member"],
			["Dynamic Link", "link_name", "in", [m.member for m in members]],
		],
		fields=[
			"name as address_name",
			"address_line1",
			"pincode",
			"city",
			"`tabDynamic Link`.link_name as member",
		],
	)
>>>>>>> 1f8e062 (perf(Current Member Data): make organization filter mandatory, filter yearly fishing permits (LAN-895) (#318))

	addresses_df = pd.DataFrame.from_records(addresses, index="member")

<<<<<<< HEAD
		# sort dataframe like report columns
		sorted_columns = [c["fieldname"] for c in self.get_columns()][1:]
		data = data[sorted_columns]
		# replace NaNs with empty strings
		data.fillna("", inplace=True)
		# convert data back to tuple
		data.reset_index(inplace=True)
		data = tuple(data.itertuples(index=False, name=None))
		return data
=======
	# merge members and addresses from different doctypes
	data = pd.concat([member_df, fishing_permits_df], axis=1).reindex(member_df.index)
	data = pd.merge(data, addresses_df, on="member", how="outer")
>>>>>>> 1f8e062 (perf(Current Member Data): make organization filter mandatory, filter yearly fishing permits (LAN-895) (#318))

	# sort dataframe like report columns
	sorted_columns = [c["fieldname"] for c in get_columns()][1:]
	data = data[sorted_columns]
	# replace NaNs with empty strings
	data = data.fillna("")
	# convert data back to tuple
	data = data.reset_index()
	data = tuple(data.itertuples(index=False, name=None))
	return data


def get_columns():
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
			"label": _("Hat Sachsen-Anhalt Erlaubnisschein"),
			"fieldtype": "Check",
			"fieldname": "has_special_yearly_fishing_permit_1",
		},
		{
			"label": _("Hat Brandenburg Erlaubnisschein"),
			"fieldtype": "Check",
			"fieldname": "has_special_yearly_fishing_permit_2",
		},
		{
			"label": _("Hat Berlin Erlaubnisschein"),
			"fieldtype": "Check",
			"fieldname": "has_special_yearly_fishing_permit_3",
		},
		{
			"label": _("Hat Mecklenburg-Vorpommern Erlaubnisschein"),
			"fieldtype": "Check",
			"fieldname": "has_special_yearly_fishing_permit_4",
		},
		{
			"label": _("Hat Saalekaskade Erlaubnisschein"),
			"fieldtype": "Check",
			"fieldname": "has_special_yearly_fishing_permit_5",
		},
		{
			"label": _("Hat LAVT Erlaubnisschein"),
			"fieldtype": "Check",
			"fieldname": "has_special_yearly_fishing_permit_6",
		},
		{
			"label": _("Hat VANT Erlaubnisschein"),
			"fieldtype": "Check",
			"fieldname": "has_special_yearly_fishing_permit_7",
		},
	]
