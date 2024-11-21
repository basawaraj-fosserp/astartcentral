// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Room Booking', {
	setup:function(frm){
		frm.set_query("select_room_type", () => {
			return { page_length: 100 };
		  });
		frm.set_query("customer", () => {
			return { page_length: 100 };
		});
	},
	refresh:function(frm){
		frm.add_custom_button(__('Check Availablity'), function() {
			window.open(`http://astartcentral.fameonu.com/app/room-booking/view/calendar/default?select_room_type=${frm.doc.select_room_type}`)
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
				console.log(r.message)
			}
		})
		frappe.call({
			method:"rental.api.check_roles",
			callback:function(r){
				if(!r.message){
					frm.set_df_property('customer', 'read_only', 1);
				}
			}
		})
	},
	from_date:function(frm){
		frm.set_value("end_date" , frm.doc.from_date)
	},
	from_time:function(frm){
		frm.set_value('end_time' , frm.doc.from_time)
		
	},
	customer:function(frm){
		frm.set_query("select_room_type", function(doc, cdt, cdn) {
			return {
				query: "rental.rental.doctype.room_booking.room_booking.get_rooms",
				filters: {
					'customer': frm.doc.customer
				}
			}
		});
	}
});