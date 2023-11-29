// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Booking Record"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		
	]
};
