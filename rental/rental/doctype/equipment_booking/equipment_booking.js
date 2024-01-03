// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Booking', {
	refresh:function(frm){
		frm.add_custom_button(__('Check Availablity'), function() {
			window.open(`https://astartcentral.fameonu.com/app/equipment-booking/view/calendar/default`)
		})
		frappe.call({
			method:"rental.rental.doctype.room_booking.room_booking.check_log_in_user",
			args:{
				user:frappe.session.user
			},
			callback:function(r){
				if (!frm.doc.customer){
					frm.set_value('customer' , r.message)
				}
			}
		})
		frm.call({
			method:"set_from_end_time",
			args:{
				self:frm.doc
			},
			callback:function(r){
				
			}
		})
		
	},
	from_date:function(frm){
		frm.set_value("to_date" , frm.doc.from_date)
	},
	from_time:function(frm){
		if(!frm.doc.to_time){
		frm.set_value('to_time' , frm.doc.from_time)
		}
	},
	customer:function(frm){
		frm.set_query("equipment", "equipment", function(doc, cdt, cdn) {
			return {
				query: "rental.rental.doctype.equipment_booking.equipment_booking.get_equipment",
				filters: {
					'customer': frm.doc.customer
				}
			}
		});
	}
});

cur_frm.fields_dict['equipment'].grid.get_field("serial_no").get_query = function(doc, cdt, cdn) {
	if(!doc.from_date || !doc.to_date || !doc.from_time || !doc.to_time){
		frappe.throw("Please select date and time")
	}

	const d = locals[cdt][cdn]
	return {
		query: "rental.rental.doctype.equipment_booking.equipment_booking.get_available_serial_no",
		filters: {
					'item': d.equipment, 
					"from_date":doc.from_date, 
					"to_date":doc.to_date, 
					"from_time":doc.from_time,
					"to_time":doc.to_time
				}
	}
}