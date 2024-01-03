// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment" ,{
	create_serial_no:function(frm){
		var d = new frappe.ui.Dialog({
			title: __('Create New Serial No'),
			fields: [
				{
					"label": "Serial No",
					"fieldname": "serial_no",
					"fieldtype": "Data",
					"reqd": 1,
				},
				{
					"label": "Equipment",
					"fieldname": "equipment",
					"fieldtype": "Link",
					"options":"Equipment",
					"read_only":1,
					"default": frm.doc.equipment_name
				},
			],
			primary_action_label: __('Create'),
			primary_action: function() {
				var data = d.get_values();
				frm.call({
					method: "create_serial_no",
					args: {
						equipment:frm.doc.equipment_name,
						serial_no:data.serial_no
					},
					callback: function(r) {
						let row = frm.add_child("serial_no");
						row.serial_no = r.message
						row.equipment = data.equipment
						frm.refresh_field("dimensions");

					d.hide()
					}
				});
			},
		});
		d.show();
	}
})

frappe.ui.form.on('Serial No List', {
	serial_no_add: function(frm,cdt,cdn) {
		let d = locals[cdt][cdn]
		d.equipment = frm.doc.equipment_name
		frm.refresh_fields('serial_no')
		frm.set_query('serial_no' , function(doc){
			return {
				filters: {"equipment":doc.equipment_name }
			}	
		
		});
	},
});