# Copyright (c) 2013, Real Experts GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
import calendar
from datetime import date
import numpy as np

def calculate_age(date_of_birth,reference_date=date.today()):
    if isinstance(date_of_birth, date):
        # source: https://www.geeksforgeeks.org/python-program-to-calculate-age-in-year/
        try:
            birthday = date_of_birth.replace(year = reference_date.year)
    
        # raised when birth date is February 29
        # and the reference year is not a leap year
        except ValueError:
            birthday = date_of_birth.replace(year = reference_date.year,
                    month = date_of_birth.month + 1, day = 1)
    
        if birthday > reference_date:
            return reference_date.year - date_of_birth.year - 1
        else:
            return reference_date.year - date_of_birth.year
    else:
        return np.nan

def determine_upcoming_birthday(date_of_birth):
    if isinstance(date_of_birth, date):
        today = date.today()
        
        if ~calendar.isleap(today.year) and (date_of_birth.month==2 and date_of_birth.day==29):
            # handle dates of birth on February 29th in a leap year
            this_years_birthday=date_of_birth.replace(year=today.year,day=28)
        else:
            # for every other date of birth
            this_years_birthday=date_of_birth.replace(year=today.year)
        # check if upcoming birthday is this year or next year
        if today<=this_years_birthday:
            upcoming_birthday=this_years_birthday
        else:
            upcoming_birthday=this_years_birthday.replace(year=today.year+1)
        return upcoming_birthday
    else:
        return np.nan

def determine_decadal_birthday(date_of_birth,upcoming_birthday=None):
    if isinstance(date_of_birth, date) and isinstance(upcoming_birthday, date):
        if upcoming_birthday is None:
            upcoming_birthday=determine_upcoming_birthday(date_of_birth)
        age_at_upcoming_birthday=calculate_age(date_of_birth,reference_date=upcoming_birthday)
        return int((age_at_upcoming_birthday%10)==0)
    else:
        return np.nan


class LANDAMemberFunction(object):
    def __init__(self, filters):
        #set filters
        
        def add_key_from_filters(key,dict):
            if key in filters:
                dict[key]=filters[key]
        #self.filter_name = {}
        #for n in ['first_name', 'last_name']:
        #    add_key_from_filters(n,self.filter_name)
        self.filter_member_function={}
        add_key_from_filters('organization',self.filter_member_function)
        add_key_from_filters('member_function_category',self.filter_member_function)
        #print(filters)

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

        def aggregate_entries(df,aggregate_field,groupby='member',sort_by=None):
            if sort_by is not None:
                df=df.sort_values(sort_by)
            aggregate_dict={}
            for k in list(df):
                aggregate_dict[k]='first'
            aggregate_dict[aggregate_field]=', '.join
            df=df.groupby(groupby).agg(aggregate_dict)
            return df

        # load member functions from db
        member_function_fields=['member', 'member_function_category','status']#'member_first_name', 'member_last_name','start_date','end_date'
        member_functions=frappe.db.get_list('Member Function', 
        filters=self.filter_member_function, 
        fields=member_function_fields, 
        as_list=True)

        # convert to pandas dataframe
        member_functions_df=frappe_tuple_to_pandas_df(member_functions,member_function_fields)

        # drop all members in dataframe that are not active
        member_functions_df=member_functions_df[member_functions_df["status"]=="Active"]
        member_functions_df.drop("status", axis=1,inplace=True)

        # merge duplicate member function catgories and seperate by comma
        #aggregate_dict={}
        #for mff in list(member_functions_df):
        #    aggregate_dict[mff]='first'
        #aggregate_dict['member_function_category']=', '.join
        #member_functions_df=member_functions_df.groupby('member').agg(aggregate_dict)
        member_functions_df=aggregate_entries(member_functions_df,'member_function_category')

        # define the labels of db entries that are supposed to be loaded
        link_field_label="`tabDynamic Link`.link_name as member"
        member_ids, link_filters = get_link_filters(member_functions)
        reindex_df=member_functions_df

        # define the member master data that are supposed to be loaded
        member_fields = ["name",'first_name', 'last_name', "date_of_birth",'organization','organization_name',]
        members=frappe.db.get_list('LANDA Member', 
        #filters=self.filter_member, 
        fields=member_fields, 
        as_list=True)
        # convert to pandas dataframe
        member_df=frappe_tuple_to_pandas_df(members,['member']+member_fields[1:])
        # calculate todays age from birth date
        member_df['age']=[calculate_age(bd) for bd in member_df['date_of_birth'].values]
        # calculate upcoming birthday
        member_df['upcoming_birthday']=[determine_upcoming_birthday(bd) for bd in member_df['date_of_birth'].values]
        # determine if decadal birthday
        member_df['is_decadal_birthday']=[determine_decadal_birthday(bd,ubd) for bd,ubd in zip(member_df['date_of_birth'].values,member_df['upcoming_birthday'].values)]

        # load awards from db
        award_fields = ["award_type", "issue_date","member"]
        awards = frappe.get_list("Award", fields=award_fields, 
        as_list=True)
        # convert to pandas dataframe
        awards_df=frappe_tuple_to_pandas_df(awards,award_fields)
        awards_df['award_list']=[at+' '+str(ad.year) for at,ad in zip(awards_df['award_type'].values,awards_df['issue_date'].values)]
        awards_df=aggregate_entries(awards_df,aggregate_field='award_list',sort_by=['issue_date'])
        awards_df.drop(award_fields[:-1], axis=1,inplace=True)

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
        data=pd.concat([member_df, member_functions_df, contacts_df, addresses_df,awards_df], axis=1).reindex(reindex_df.index)
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
            "fieldname": "date_of_birth",
            "fieldtype": "Date",
            "label": "Date of Birth"
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
            "fieldname": "member_age",
            "fieldtype": "Data",
            "label": "Age"
            },
            {
            "fieldname": "upcoming_birthday",
            "fieldtype": "Date",
            "label": "Upcoming Birthday"
            },
            {
            "fieldname": "is_decadal_birthday",
            "fieldtype": "Check",
            "label": "Is Decadal Birthday"
            },
            {
            "fieldname": "member_function_category",
            "fieldtype": "Data",
            "label": "Member Function Categories"
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
            },
            {
            "fieldname": "award_list",
            "fieldtype": "Data",
            "label": "Award List"
            }
        ]

def execute(filters=None):
    return LANDAMemberFunction(filters).run()