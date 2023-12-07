frappe.pages['Booking Page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Room Booking',
		single_column: true
	});
	frappe.booking_page.make(page);
	page.posting_date_field = page.add_field({
        fieldname: 'from_date',
		label: __('From date'),
		fieldtype:'Date',
        default:"Today"
	});
	page.posting_date_field = page.add_field({
        fieldname: 'to_date',
		label: __('To date'),
		fieldtype:'Date',
        default:"Today"
	});
	page.posting_date_field = page.add_field({
        fieldname: 'check',
		label: __('Check Availability'),
		fieldtype:'Button',
	});
}
frappe.booking_page = {
	start: 0,
	make: function(page) {
		var me = frappe.booking_page;
		me.page = page;
		me.body = $('<div></div>').appendTo(me.page.main);
		var data = "";
		$(frappe.render_template('booking_page', data)).appendTo(me.body);
		this.page.main.find(".btn-create-file").on('click', function() {
			frappe.call({
				method
			})
		})
	},
}