# Copyright (c) 2024, Viral Patel and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = [
			{
			'label': "Customer",
			'fieldname': "customer",
			'fieldtype': "Link",
			'options': 'Customer',
			'width': 300  ,
			}, 
			{
			'label': "Room Name",
			'fieldname': "select_room_type",
			'fieldtype': "Data",
			'width': 300  ,
			},
			{
			'label': "Number Of Booking",
			'fieldname': "number_of_booking",
			'fieldtype': "Float",
			'width': 100  ,
			}
		]

	condition = ''

	if filters.get('from_date'):
		condition = condition + "and from_date >= '{0}'".format(filters.get('from_date'))
	if filters.get('from_date'):
		condition = condition + "and end_date <= '{0}'".format(filters.get('end_date'))
	if filters.get('customer'):
		condition = condition + "and customer = '{0}'".format(filters.get('customer'))
		
	result = frappe.db.sql(f"""
						Select select_room_type , count(select_room_type) as number_of_booking , customer
						From `tabRoom Booking`
						Where docstatus = 1 {condition}
						Group by customer , select_room_type
						""",as_dict=1)
						

	return columns, result