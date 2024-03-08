// Copyright (c) 2024, Viral Patel and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Room Booked Max No of Times"] = {
	"filters": [
		{
			"label": "Customer",
			"fieldtype": "Link",
			"fieldname": "customer",
			"options": "Customer",
		},
		{
			"label": "From Date",
			"fieldtype": "Date",
			"fieldname": "from_date",
		},
		{
			"label": "End Date",
			"fieldtype": "Date",
			"fieldname": "end_date",
		}
	]
};
