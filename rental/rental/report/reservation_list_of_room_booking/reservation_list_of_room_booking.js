// Copyright (c) 2024, Viral Patel and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Reservation List of Room Booking"] = {
	"filters": [
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
			'fieldname': "from_date",
			'fieldtype': "Date",
			'width': 200,
		},
		{
			'label': "End Date",
			'fieldname': "end_date",
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
