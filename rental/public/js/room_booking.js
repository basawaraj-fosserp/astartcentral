frappe.ready(function () {
        frappe.call({
            method:"rental.rental.doctype.room_booking.room_booking.check_log_in_user",
            args:{
                user:frappe.session.user
            },
            callback:function(r){
                console.log(r.message)
                if(r.message){
                    var customerField = document.querySelector('div[data-fieldname="customer"]');
                    var customerInput = customerField.querySelector('input');
                    customerInput.value = r.message;
                }
            }
        });
});
