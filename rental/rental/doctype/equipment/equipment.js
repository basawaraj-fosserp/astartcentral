// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment', {
	refresh: function(frm) {
		frm.add_custom_button(__("Update Equipment Qty"), function() {
			console.log('remove')
			var d = new frappe.ui.Dialog({
				title: __('Update Equipment Qty'),
				fields: [
					{
						"label" : "Company",
						"fieldname": "company",
						"fieldtype": "Link",
						"options":"Company",
						"default": frappe.defaults.get_default('Company')
					},
					{
						"label" : "Equipment",
						"fieldname": "equipment",
						"fieldtype": "Data",
						"read_only": 1,
						"default": frm.doc.name
					},
					{
						"label" : "Quantity",
						"fieldname": "qty",
						"fieldtype": "Float",
					},
				],
				primary_action_label: 'Update',
				primary_action() {
					var data = d.get_values();
					frappe.call({
						method : "rental.api.update_stock_of_equipment",
						args:{
							item : data.equipment,
							qty : data.qty,
							company : data.company
						}
					})


					d.hide();
				}
			});
			d.show();			
		});
	}
});