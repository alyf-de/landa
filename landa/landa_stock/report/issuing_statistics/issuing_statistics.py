# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
from frappe import _


def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "delivered_qty",
			"label": _("Delivered Qty"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2,
		},
		{
			"fieldname": "delivered_amount",
			"label": _("Delivered Amount"),
			"fieldtype": "Currency",
			"width": 170,
		},
		{
			"fieldname": "returned_qty",
			"label": _("Returned Qty"),
			"fieldtype": "Float",
			"width": 180,
			"precision": 2,
		},
		{
			"fieldname": "returned_amount",
			"label": _("Returned Amount"),
			"fieldtype": "Currency",
			"width": 170,
		},
		{
			"fieldname": "net_delivered_qty",
			"label": _("Net Delivered Qty"),
			"fieldtype": "Float",
			"width": 150,
			"precision": 2,
		},
		{
			"fieldname": "net_delivered_amount",
			"label": _("Net Delivered Amount"),
			"fieldtype": "Currency",
			"width": 170,
		},
		{
			"fieldname": "average_rate",
			"label": _("Average Rate"),
			"fieldtype": "Currency",
			"width": 180,
		},
	]


def get_data(filters):
	dn_items = frappe.get_list(
		"Delivery Note",
		fields=[
			"is_return",
			"`tabDelivery Note Item`.item_code",
			"`tabDelivery Note Item`.item_name",
			"`tabDelivery Note Item`.qty",
			"`tabDelivery Note Item`.base_net_amount",
		],
		filters=filters,
	)

	if not dn_items:
		return []

	df = pd.DataFrame.from_records(dn_items)
	df["returned_qty"] = df["qty"].abs().where(df["is_return"] == 1, 0)
	df["returned_amount"] = df["base_net_amount"].abs().where(df["is_return"] == 1, 0)

	df["qty"] = df["qty"].where(df["is_return"] == 0, 0)
	df["base_net_amount"] = df["base_net_amount"].where(df["is_return"] == 0, 0)

	df.drop(columns=["is_return"], inplace=True)

	df = df.groupby(["item_code", "item_name"]).sum().reset_index()
	df["net_delivered_qty"] = df["qty"] - df["returned_qty"]
	df["net_delivered_amount"] = df["base_net_amount"] - df["returned_amount"]

	df["average_rate"] = df["net_delivered_amount"] / df["net_delivered_qty"]

	return df.values.tolist()


def build_filters(filters):
	_filters = [
		["Delivery Note", "docstatus", "=", 1],
	]

	if filters.get("year_of_settlement"):
		_filters.append(["Delivery Note", "year_of_settlement", "=", filters["year_of_settlement"]])

	if filters.get("customer"):
		_filters.append(["Delivery Note", "customer", "=", filters["customer"]])

	if filters.get("item_code"):
		_filters.append(["Delivery Note Item", "item_code", "=", filters["item_code"]])

	return _filters


def execute(filters=None):
	_filters = build_filters(filters)
	return get_columns(), get_data(_filters)
