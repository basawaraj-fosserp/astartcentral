// Function to refresh the page
function refreshPage() {
    
    location.reload(true); // Passing true forces a reload from the server, not from the cache
}
setInterval(refreshPage, 100000);


frappe.ready(function() {
    var element = document.querySelector('.main-bg-screen')
    var main_ele = element.querySelector('.center-div')
    var h1element = main_ele.querySelector('h1')
    frappe.call({
        method:"rental.rental.web_template.show_booking_availability.get_booking_data.current_room_booking_data",
        args:{
            room:h1element.innerHTML
        },
        callback:function(r){
            if(r.message){
                var current_time = document.querySelector('.current_time')
                current_time.innerHTML = r.message.current_time
                var current_date = document.querySelector('.current_date')
                current_date.innerHTML = r.message.today
                var available = document.querySelector('.available')
                available.innerHTML = r.message.availability
                var uptiming = document.querySelector('.uptiming')
                uptiming.innerHTML = r.message.event
                var title_reservation = document.querySelector('.title_reservation')
                title_reservation.innerHTML = r.message.title
            }
        }
    })
})