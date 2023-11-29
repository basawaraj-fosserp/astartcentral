// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Room Booking', {
	refresh:function(frm){
		frm.add_custom_button(__('Check Availablity'), function() {
			window.open("http://astartcentral.fameonu.com/app/room-booking/view/calendar/default")
		})
		
	}
});
