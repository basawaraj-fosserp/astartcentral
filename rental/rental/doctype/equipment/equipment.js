// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment', {
	refresh: function(frm) {
		frm.add_custom_button(__("Update Equipment Qty"), function() {
			var d = new frappe.ui.Dialog({
				title: __('Update Equipment Qty'),
				fields: [
					{
						"label" : "Equipment",
						"fieldname": "equipment",
						"fieldtype": "Data",
						"read_only": 1,
						"default": frm.doc.name
					},
					{
						"label" : "Available Quantity",
						"fieldname": "available_qty",
						"fieldtype": "Float",
						"read_only":1,
						onload: function () {
							frappe.call({
								method : "rental.api.check_equipment_stock",
								args:{
									item : frm.doc.name
								}
							}).then(r => {
								field.df.default = r.message;
								field.refresh();
							})
							
						}
					},
				],
			});
		});
	}
});
