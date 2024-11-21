// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Booking', {
	setup:function(frm){
		frm.set_query("equipment", "equipment", () => {
			return { page_length: 100 };
		  });
	},
	refresh:function(frm){
		frappe.call({
			method:"rental.rental.doctype.room_booking.room_booking.check_log_in_user",
			args:{
				user:frappe.session.user
			},
			callback:function(r){
				if (!frm.doc.customer){
					frm.set_value('customer' , r.message)
				}
				if(r.message){
					frm.set_df_property('customer', 'hidden', 1);
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