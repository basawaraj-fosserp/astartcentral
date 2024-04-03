// Copyright (c) 2024, Viral Patel and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Credit Ledger"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"warehouse",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				const company = frappe.query_report.get_filter_value('company');
				return {
					filters: { 
						'company': company,
						'is_group':0,
						'disabled':0,
						'parent_warehouse':''
					}
				}
			}
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "out_qty" && data && data.out_qty < 0) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
			value = "<span style='color:green'>" + value + "</span>";
		}

		return value;
	},
	onload:function(){
		frappe.call({
			method:"rental.rental.report.credit_ledger.credit_ledger.get_user_roll",
			args:{
				user : frappe.session.user
			},
			callback:function(r){
				if (r.message){
					var element = document.querySelector('div[data-fieldname="warehouse"]')
					element.style.display ="none";
				}
			}
		})
	}
};

erpnext.utils.add_inventory_dimensions('Stock Ledger', 10);
