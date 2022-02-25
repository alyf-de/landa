# Copyright (c) 2022, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd

class WaterBodyManagement(object):
	def __init__(self, filters):
		self.filters=filters

	def run(self):
		return self.get_columns(), self.get_data()

	def get_data(self):
		def frappe_tuple_to_pandas_df(frappe_tuple,fields):
			# convert to pandas dataframe
			df=pd.DataFrame(frappe_tuple,columns=fields)
			# set by member ID as dataframe index
			df.set_index('member',inplace=True)
			return df

		def remove_duplicate_indices(df,index='member', sort_by=None,keep='last'):
			"""Remove rows in dataframe with duplicate indeces. 
			If sort_by is specified the dataframe is firsted sorted by these columns keeping the entry specified in keep, e.g. 'last'"""
			if sort_by is not None:
				df=df.sort_values(sort_by)
			return df.reset_index().drop_duplicates(subset=[index],keep=keep).set_index(index)

		def get_link_filters(frappe_tuple,index=0):
			member_ids=[m[index] for m in frappe_tuple] # list of member names (ID)
			link_filters = [
					["Dynamic Link", "link_doctype", "=", "LANDA Member"],
					["Dynamic Link", "link_name", "in", member_ids],
				]
			return member_ids,link_filters

		# load water body management from db
		wbm_fields=['water_body',"water_body_title","fishing_area",
		'organization',"organization_name",'status','member','first_name','last_name']
		wbm=frappe.get_list(
			"Water Body Management Local Organization",
			fields=[
				"water_body",
				"water_body_title",
				"fishing_area",
				"organization",
				"organization_name",
				"status",
				"`tabWater Body Local Contact Table`.landa_member",
				"`tabWater Body Local Contact Table`.first_name",
				"`tabWater Body Local Contact Table`.last_name",
				],
				filters=self.filters,
				as_list=True
				)

		# convert to pandas dataframe
		wbm_df=frappe_tuple_to_pandas_df(wbm,wbm_fields)

		# drop all lines in dataframe that are not active
		wbm_df=wbm_df[wbm_df["status"]=="Active"]
		wbm_df.drop("status", axis=1,inplace=True)

		# define the labels of db entries that are supposed to be loaded
		link_field_label="`tabDynamic Link`.link_name as member"
		member_ids, link_filters = get_link_filters(wbm,index=3)
		reindex_df=wbm_df

		# load addresses from db	
		address_fields = ["address_line1", "pincode", "city", "is_primary_address"]
		addresses = frappe.get_list("Address", filters=link_filters, fields=address_fields+[link_field_label], 
		as_list=True)
		# convert to pandas dataframe
		addresses_df=frappe_tuple_to_pandas_df(addresses,address_fields+["member"])
		# remove all duplicate addresses by keeping only the primary address or last existing address if there is no primary address
		addresses_df=remove_duplicate_indices(addresses_df,sort_by='is_primary_address')

		# merge all columns to one address column and add this as the first column
		addresses_df['full_address']=addresses_df["address_line1"]+', '+addresses_df["pincode"]+' '+addresses_df["city"]
		address_cols=addresses_df.columns.tolist()
		addresses_df = addresses_df[address_cols[-1:] + address_cols[:-1]]
		# remove column 'is_primary_address'
		addresses_df.drop('is_primary_address', axis=1,inplace=True)

		# load contacts from db that are linked to the member fucntions loaded before
		contact_fields = ["email_id", "phone", "mobile_no"]
		contacts = frappe.get_list("Contact", filters=link_filters, fields=contact_fields+[link_field_label], 
		as_list=True)
		# convert to pandas dataframe
		contacts_df=frappe_tuple_to_pandas_df(contacts,contact_fields+["member"])
		contacts_df=remove_duplicate_indices(contacts_df)
		
		# merge all dataframes from different doctypes and load data of all members without member functions only if necessary
		data=pd.concat([wbm_df, contacts_df, addresses_df], axis=1).reindex(reindex_df.index)
		# sort columns as needed
		data=data.reindex(['first_name', 'last_name', 'organization','organization_name',
		'water_body','water_body_name', 'email_id', 'phone', 'mobile_no',
		'full_address', 'address_line1', 'pincode', 'city'],
		axis=1)
		# replace NaNs with empty strings
		data.fillna('', inplace=True)

		# convert data back to tuple
		data.reset_index(inplace=True)
		data=tuple(data.itertuples(index=False, name=None))
		return data

	def get_columns(self):
		return [
			{
			"fieldname": "landa_member",
			"fieldtype": "Link",
			"options": "LANDA Member",
			"label": "Member"
			},
			{
			"fieldname": "first_name",
			"fieldtype": "Data",
			"label": "First Name"
			},
			{
			"fieldname": "last_name",
			"fieldtype": "Data",
			"label": "Last Name"
			},
			{
			"fieldname": "organization",
			"fieldtype": "Link",
			"options": "Organization",
			"label": "Organization"
			},
			{
			"fieldname": "water_body",
			"fieldtype": "Link",
			"label": "Water Body",
			"options": "Water Body"
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
			},
			{
			"fieldname": "full_address",
			"fieldtype": "Data",
			"label": "Primary Address (Full)"
			},
			{
			"fieldname": "address_line1",
			"fieldtype": "Data",
			"label": "Address Line 1"
			},
			{
			"fieldname": "pincode",
			"fieldtype": "Data",
			"label": "Pincode"
			},
			{
			"fieldname": "city",
			"fieldtype": "Data",
			"label": "City"
			}
		]

def execute(filters=None):
	return WaterBodyManagement(filters).run()