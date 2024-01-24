// Function to refresh the page
function refreshPage() {
    
    location.reload(true); // Passing true forces a reload from the server, not from the cache
}
setInterval(refreshPage, 30000);


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
                var data = r.message
                var current_time = document.querySelector('.current_time')
                current_time.innerHTML = data.current_time
                var current_date = document.querySelector('.current_date')
                current_date.innerHTML = data.today
                var available = document.querySelector('.available')
                available.innerHTML = data.availability
                if (data.availability == 'NOT AVAILABLE'){
                    var innerbox2 = document.querySelector('.inner-box2')
                    innerbox2.classList.add('inner-box2not-available')
                }
                else{
                    var innerbox2 = document.querySelector('.inner-box2')
                    innerbox2.classList.add('inner-box2available')
                }
                console.log(data)
                if (data.current_booking){
                    var center_main_element = document.querySelector('.center-div')
                    var title_of_current = document.createElement('p');
                    title_of_current.innerHTML = data.current_booking.title_of_reservation
                    var current_log = document.createElement('b');
                    current_log.innerHTML = data.current_booking.from_time + " "+ data.current_booking.end_time
                    var contact_title = document.createElement('p');
                    var contact_name = document.createElement('b');
                    contact_title.innerHTML = "Meeting Leader"
                    contact_name.innerHTML = data.current_booking.contact_name  
                    center_main_element.append(title_of_current)
                    center_main_element.append(current_log)
                    center_main_element.append(contact_title)
                    center_main_element.append(contact_name)
                }
                if(data.event.length > 0 && data.event != "No Upcomming Event"){
                    var main_element = document.querySelector('.inner-box3')
                    data.event.forEach(a => {
                        var titleReservation = document.createElement('h3');
                        titleReservation.className = 'title_reservation';
                        titleReservation.innerHTML = a.title_of_reservation
                        main_element.appendChild(titleReservation);

                        var timelog = document.createElement('h3');
                        timelog.className = 'uptiming';
                        timelog.innerHTML = a.from_time + " - "+ a.end_time
                        main_element.appendChild(timelog);

                    });
                }
                else{
                    var main_element = document.querySelector('.inner-box3')
                    var titleReservation = document.createElement('span');
                    titleReservation.innerHTML = "No Upcomming Event"
                    main_element.appendChild(titleReservation)
                }
            }
        }
    })
})