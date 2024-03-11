// Copyright (c) 2024, Viral Patel and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer subscription expiry"] = {
	"filters": [
		{
			'label': "Customer",
			'fieldname': "party",
			'fieldtype': "Link",
			'options': 'Customer',
			'width': 200  ,
		},
	]
};
