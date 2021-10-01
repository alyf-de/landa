# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
from datetime import date
import numpy as np
import time

class Address(object):
    def __init__(self, filters):
        #set filters
        self.filter_name = {}
        def add_key_from_filters(key,dict):
            if key in filters:
                dict[key]=filters[key]
        for n in ['first_name', 'last_name']:
            add_key_from_filters(n,self.filter_name)
        self.filter_member=self.filter_name.copy()
        add_key_from_filters('organization',self.filter_member)

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

        def get_link_filters(frappe_tuple):
            member_ids=[m[0] for m in frappe_tuple] # list of member names (ID)
            link_filters = [
                    ["Dynamic Link", "link_doctype", "=", "LANDA Member"],
                    ["Dynamic Link", "link_name", "in", member_ids],
                ]
            #print(member_ids,link_filters)
            return member_ids,link_filters

        # define the member master data that are supposed to be loaded
        member_fields = ["name",'first_name', 'last_name', 'organization','organization_name',]
        members=frappe.db.get_list('LANDA Member', 
        filters=self.filter_member, 
        fields=member_fields, 
        as_list=True)
        
        # convert to pandas dataframe
        member_df=frappe_tuple_to_pandas_df(members,['member']+member_fields[1:])

        # define the labels of db entries that are supposed to be loaded
        link_field_label="`tabDynamic Link`.link_name as member"
        member_ids, link_filters = get_link_filters(members)

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
        # remove column 'is_primary_address'
        addresses_df.drop('is_primary_address', axis=1,inplace=True)
        
        # merge all dataframes from different doctypes 
        data=pd.concat([member_df, addresses_df], axis=1).reindex(member_df.index)
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
            "fieldname": "organization_name",
            "fieldtype": "Data",
            "label": "Organization Name"
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
            },
            {
            "fieldname": "full_address",
            "fieldtype": "Data",
            "label": "Primary Address (Full)"
            }
        ]

def execute(filters=None):
    return Address(filters).run()