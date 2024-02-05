// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Credit Request', {
	refresh: function(frm) {
		frappe.call({
			method:"rental.rental.doctype.room_booking.room_booking.check_log_in_user",
			args:{
				user:frappe.session.user
			},
			callback:function(r){
				if (!frm.doc.customer){
					frm.set_value('customer' , r.message)
					frm.set_df_property('customer', 'read_only', 1);
				}
			}
		})
		frappe.call({
			method:"rental.api.check_roles",
			callback:function(r){
				if (r.message && frm.doc.status != "Allocated"){
					frm.add_custom_button(__('Credit Allocation'), function() {
						frappe.model.open_mapped_doc({
							method:"rental.rental.doctype.credit_request.credit_request.create_credit_allocation",
							frm:frm
						})
					})
				}
			}
		})
	}
});
