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
			'width': 200  ,
		},
		{
			'label': "Equipment",
			'fieldname': "equipment",
			'fieldtype': "Link",
			'options': 'Equipment',
			'width': 200,
		},
		{
			'label': "From Date",
			'fieldname': "from_datetime",
			'fieldtype': "Datetime",
			'width': 200,
		},
		{
			'label': "to Date",
			'fieldname': "to_datetime",
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
		condition += f" and eb.customer = '{filters.get('customer')}'"
	if filters.get('status'):
		condition += f" and eb.status = '{filters.get('status')}'"
	if filters.get('from_date'):
		condition += f" and eb.from_date >= '{filters.get('from_date')}'"
	if filters.get('to_date'):
		condition += f" and eb.to_date <= '{filters.get('to_date')}'"
	if filters.get('equipment'):
		condition += f" and ei.equipment = '{filters.get('equipment')}'"



	data = frappe.db.sql(f""" 
			Select eb.from_datetime, eb.to_datetime, eb.customer, eb.status, ei.equipment
			From `tabEquipment Booking` as eb
			Left Join `tabEquipment Items` as ei ON ei.parent = eb.name
			where eb.docstatus = 1 {condition}
		""",as_dict = 1)
		
	return columns, data
