// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Booking', {
	refresh:function(frm){
		frm.add_custom_button(__('Check Availablity'), function() {
			window.open("http://astartcentral.fameonu.com/app/equipment-booking/view/calendar/default")
		})
		
	},
	from_date:function(frm){
		frm.set_value("to_date" , frm.doc.from_date)
	}
});
