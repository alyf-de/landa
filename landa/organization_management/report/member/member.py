# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd

MEMBER_FIELDS = [
	"name",
	"first_name",
	"last_name",
	"organization",
	"organization_name",
]


class Member:
	def __init__(self, filters):
		self.filter_member = []

		for key in ["name", "first_name", "last_name", "organization"]:
			if key in filters:
				self.filter_member.append([key, "like", "%" + filters[key] + "%"])

		self.members = None
		self.members_df = None

	def run(self):
		return self.get_columns(), self.get_data()

	def set_members(self):
		self.members = frappe.db.get_list(
			"LANDA Member",
			filters=self.filter_member,
			fields=MEMBER_FIELDS,
			as_list=True,
		)

		# convert to pandas dataframe
		self.members_df = pd.DataFrame(self.members, columns=["member"] + MEMBER_FIELDS[1:])
		self.members_df.set_index("member", inplace=True)


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
