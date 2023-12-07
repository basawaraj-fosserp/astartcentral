frappe.ready(function () {
    frappe.call({
        method:"rental.rental.doctype.room_booking.room_booking.check_log_in_user",
        args:{
            user:frappe.session.user
        },
        callback:function(r){
            if(r.message){
                var customerField = document.querySelector('div[data-fieldname="customer"]');
                var customerInput = customerField.querySelector('input');
                customerInput.value = r.message;
            }
        }
    });
    frappe.web_form.after_insert = () =>  {
        let data = frappe.web_form.get_values();
        doc = frappe.get_doc("Room Booking" ,{
            "customer":data.customer,
            "end_date":data.end_date,
            "end_time":data.end_time,
            "from_date":data.from_date,
            "from_time":data.from_time,
            "select_room_type":data.select_room_type
        })
        console.log(doc)
    }
    
});
