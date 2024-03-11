# Copyright (c) 2024, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now , getdate


def execute(filters=None):
	columns = [
		{
			'label': "Customer",
			'fieldname': "party",
			'fieldtype': "Link",
			'options': 'Customer',
			'width': 200  ,
		},
		{
			'label': "Start date",
			'fieldname': "start_date",
			'fieldtype': "Date",
			'width': 200  ,
		},
		{
			'label': "End date",
			'fieldname': "end_date",
			'fieldtype': "Date",
			'width': 200  ,
		},
		{
			'label': "Remaining Days",
			'fieldname': "remaining_days",
			'fieldtype': "Data",
			'width': 200  ,
		}
	]
	condition = ''
	if filters.get('party'):
		condition = f"and party  = '{filters.get('party')}'"
	data = frappe.db.sql(f""" 
						Select name, party, start_date, end_date
						From `tabSubscription`
						Where status != 'Cancelled' and party_type = 'Customer' and end_date > '{str(getdate())}' {condition}
						Order By end_date
						 """,as_dict= 1)
	
	

	for row in data:
		day_diff = (row.end_date - getdate()).days
		row.update({'remaining_days': day_diff})

	return columns, data
