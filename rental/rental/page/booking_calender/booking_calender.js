frappe.pages['booking-calender'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		single_column: true
	});
	frappe.booking_calender.make(page);
	page.year_field = page.add_field({
        fieldname: 'year',
		label: __('Year'),
		fieldtype:'Select',
		options:['2023','2024','2025','2026','2027','2028']
        
	});
	page.year_field = page.add_field({
        fieldname: 'year',
		label: __('Year'),
		fieldtype:'Select',
		options:['2023','2024','2025','2026','2027','2028']
        
	});
}

frappe.booking_calender = {
	make: function(page) {
		var me = frappe.booking_calender;
		me.page = page;
		me.body = $('<div></div>').appendTo(me.page.main);
		data=""
		this.page.main.find(".btn-create-file").on('onchange', function() {
			console.log("html change")
		})
		$(frappe.render_template('booking_calender', data)).appendTo(me.body);
	}
}
