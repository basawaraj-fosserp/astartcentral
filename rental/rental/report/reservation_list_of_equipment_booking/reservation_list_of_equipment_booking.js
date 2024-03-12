// Copyright (c) 2024, Viral Patel and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Reservation List of Equipment Booking"] = {
	"filters": [
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
			'fieldname': "from_date",
			'fieldtype': "Date",
			'width': 200,
		},
		{
			'label': "To Date",
			'fieldname': "to_date",
			'fieldtype': "Date",
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
};
