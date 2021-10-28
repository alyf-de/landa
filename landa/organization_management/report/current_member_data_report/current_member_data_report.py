# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
from datetime import date
import numpy as np

class LANDACurrentMemberData(object):
    def __init__(self, filters):
        # set attribute to load only members and remove it from filters
        self.filter=filters.pop('organization', None)

    def run(self):
        return self.get_columns(), self.get_data()

    def get_data(self):
        def frappe_tuple_to_pandas_df(frappe_tuple,fields):
            # convert to pandas dataframe
            df=pd.DataFrame(frappe_tuple,columns=fields)
            # set by member ID as dataframe index
            df.set_index('member',inplace=True)
            return df

        def get_link_filters(frappe_tuple):
            member_ids=[m[0] for m in frappe_tuple] # list of member names (ID)
            link_filters = [
                    ["Dynamic Link", "link_doctype", "=", "LANDA Member"],
                    ["Dynamic Link", "link_name", "in", member_ids],
                ]
            return member_ids,link_filters

        # define the member master data that are supposed to be loaded
        member_fields = ["name",'last_name', 'first_name', "date_of_birth",'organization',
                        'is_supporting_member','has_key',
                        'has_special_yearly_fishing_permit_1','has_special_yearly_fishing_permit_2','additional_information']
        members=frappe.db.get_list('LANDA Member', 
        filters=self.filter, 
        fields=member_fields, 
        as_list=True)
        # convert to pandas dataframe
        member_df=frappe_tuple_to_pandas_df(members,['member']+member_fields[1:])
        # create empty clomuns for yearly fishing permit
        fishing_permit_columns=['year','type','date_of_issue','number']
        for c in fishing_permit_columns:
            member_df[c]=np.nan
        
        # define the labels of db entries that are supposed to be loaded
        link_field_label="`tabDynamic Link`.link_name as member"
        member_ids, link_filters = get_link_filters(members)
        # load addresses from db    
        address_fields = ["name","address_line1", "pincode", "city"]
        addresses = frappe.get_list("Address", filters=link_filters, fields=address_fields+[link_field_label], 
        as_list=True)
        # convert to pandas dataframe
        addresses_df=frappe_tuple_to_pandas_df(addresses,address_fields+["member"])
        # rename index column
        addresses_df.rename({'name': 'address_name'}, axis=1, inplace=True)
        
        # merge members and addresses from different doctypes
        data=pd.merge(member_df,addresses_df, on='member',how='outer')

        # sort dataframe like report columns
        sorted_columns=[c['fieldname'] for c in self.get_columns()][1:]
        data=data[sorted_columns]
        # replace NaNs with empty strings
        data.fillna('', inplace=True)
        # convert data back to tuple
        data.reset_index(inplace=True)
        data=tuple(data.itertuples(index=False, name=None))
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
            "fieldtype": "Data",
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
            "label": "Additional Information",
            "fieldtype": "Data",
            "fieldname": "additional_information",
            }
            ]

def execute(filters=None):
    return LANDACurrentMemberData(filters).run()
