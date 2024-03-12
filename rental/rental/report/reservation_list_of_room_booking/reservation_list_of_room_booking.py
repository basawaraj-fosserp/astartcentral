# Copyright (c) 2024, Viral Patel and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []

	columns = [
		{
			'label': "Customer",
			'fieldname': "customer",
			'fieldtype': "Link",
			'options': 'Customer',
			'width': 200  ,
		},
		{
			'label': "Room",
			'fieldname': "room",
			'fieldtype': "Link",
			'options': 'Room',
			'width': 200,
		},
		{
			'label': "From Date",
			'fieldname': "from_datetime",
			'fieldtype': "Datetime",
			'width': 200,
		},
		{
			'label': "End Date",
			'fieldname': "end_datetime",
			'fieldtype': "Datetime",
			'width': 200,
		},
		{
			'label': "Status",
			'fieldname': "status",
			'fieldtype': "Select",
			'options': ['Active' ,'Inactive'],
			'width': 200 ,
		}
	]
	condition = ''
	if filters.get('customer'):
		condition += f" and customer = '{filters.get('customer')}'"
	if filters.get('status'):
		condition += f" and status = '{filters.get('status')}'"
	if filters.get('from_date'):
		condition += f" and from_date >= '{filters.get('from_date')}'"
	if filters.get('end_date'):
		condition += f" and end_date <= '{filters.get('end_date')}'"
	if filters.get('room'):
		condition += f" and select_room_type = '{filters.get('room')}'"

	data = frappe.db.sql(f""" 
		Select customer, from_datetime, end_datetime, select_room_type as room , status
		From `tabRoom Booking`
		where  docstatus = 1 {condition}
	""",as_dict = 1)

	return columns, data
