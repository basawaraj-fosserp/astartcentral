// Converts a hex color (#rgb or #rrggbb) to an rgba() string with the given opacity
function hexToRgba(hex, opacity) {
    hex = hex.replace('#', '')
    if (hex.length === 3) {
        hex = hex.split('').map(c => c + c).join('')
    }
    var r = parseInt(hex.substring(0, 2), 16)
    var g = parseInt(hex.substring(2, 4), 16)
    var b = parseInt(hex.substring(4, 6), 16)
    return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + opacity + ')'
}

// Function to refresh the page
function refreshPage() {
    
    location.reload(true); // Passing true forces a reload from the server, not from the cache
    
}
setInterval(refreshPage, 30000);


frappe.ready(function() {
    var element = document.querySelector('.main-bg-screen')
    var main_ele = element.querySelector('.center-div')
    var h2element = main_ele.querySelector('.room_title')
    frappe.call({
        method:"rental.rental.web_template.show_booking_availability.get_booking_data.current_room_booking_data",
        args:{
            room:h2element.innerHTML
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
                var next_available_slot = document.querySelector('.next_available_slot')
                if (data.availability == 'OCCUPIED'){
                    var innerbox2 = document.querySelector('.inner-box2')
                    innerbox2.classList.add('inner-box2not-available')
                    if (data.next_available_slot){
                        next_available_slot.innerHTML = "Next Available: " + data.next_available_slot
                    }
                }
                else{
                    var innerbox2 = document.querySelector('.inner-box2')
                    innerbox2.classList.add('inner-box2available')
                }
                if (data.current_booking){
                    var center_main_element = document.querySelector('.center-div')
                    var title_of_current = document.createElement('p');
                    title_of_current.innerHTML = data.current_booking.title_of_reservation
                    title_of_current.className = "current_resevation" 
                    var current_log = document.createElement('b');
                    current_log.className = 'current_timelog'
                    current_log.innerHTML = data.current_booking.from_time + " "+ data.current_booking.end_time
                    var br = document.createElement('p');
                    br.innerHTML = '<br>'
                    var contact_title = document.createElement('p');
                    var contact_name = document.createElement('b');
                    contact_title.innerHTML = "Meeting Leader"
                    contact_title.className = "meeting_leader_label"
                    contact_name.innerHTML = data.current_booking.contact_name
                    contact_name.className = "meeting_leader_name"
                    center_main_element.append(title_of_current)
                    center_main_element.append(current_log)
                    center_main_element.append(br)
                    center_main_element.append(contact_title)
                    center_main_element.append(contact_name)
                }
                if(data.event.length > 0 && data.event != "No Upcoming Event"){
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
            applyColorSettings()
        }
    })

    function applyColorSettings() {
        frappe.call({
        method:"rental.rental.web_template.show_booking_availability.get_booking_data.get_color_code",
        callback:function(r){
            var main_bg_screen = document.querySelector('.main-bg-screen')
            if(r.message.time_date_box_background){
                main_bg_screen.style.setProperty('--time-date-box-bg', hexToRgba(r.message.time_date_box_background, 0.5))
            }
            if(r.message.availability_box_background){
                main_bg_screen.style.setProperty('--availability-box-bg', hexToRgba(r.message.availability_box_background, 0.5))
            }
            if(r.message.not_available_box_background){
                main_bg_screen.style.setProperty('--not-available-box-bg', hexToRgba(r.message.not_available_box_background, 0.5))
            }
            if(r.message.room_title_box_background){
                main_bg_screen.style.setProperty('--room-title-box-bg', hexToRgba(r.message.room_title_box_background, 0.78))
            }
            if(r.message.upcoming_box_background){
                main_bg_screen.style.setProperty('--upcoming-box-bg', hexToRgba(r.message.upcoming_box_background, 0.72))
            }

            var room_title = document.querySelector('.room_title')
            room_title.style.color = r.message.room_title

            var current_time = document.querySelector('.current_time')
            current_time.style.color = r.message.current_time

            var current_day_and_date = document.querySelector('.current_date')
            current_day_and_date.style.color = r.message.current_day_and_date

            var available = document.querySelector('.available')
            if(available.innerHTML == "OCCUPIED"){
                available.style.color = r.message.not_available
            }else{
                available.style.color = r.message.available
            }
            
            var upcoming = document.querySelector('.upcomming')
            upcoming.style.color = r.message.label_upcoming

            var title_of_reservation = document.querySelectorAll('.title_reservation')
            title_of_reservation.forEach(function(element) {
                element.style.color = r.message.title_booking
            });
            
            var uptiming = document.querySelectorAll('.uptiming')
            uptiming.forEach(function(element) {
                element.style.color = r.message.upcomming_time
            });

            var current_reservation_title = document.querySelector('.current_resevation')
            if (current_reservation_title) {
                current_reservation_title.style.color = r.message.current_reservation_title
            }

            var current_reservation_time_log = document.querySelector('.current_timelog')
            if (current_reservation_time_log) {
                current_reservation_time_log.style.color = r.message.current_reservation_time_log
            }

            var meeting_leader_label = document.querySelector('.meeting_leader_label')
            if (meeting_leader_label) {
                meeting_leader_label.style.color = r.message.meeting_leader_label
            }

            var meeting_leader_name = document.querySelector('.meeting_leader_name')
            if (meeting_leader_name) {
                meeting_leader_name.style.color = r.message.meeting_leader_name
            }

            var next_available_slot = document.querySelector('.next_available_slot')
            if (next_available_slot) {
                next_available_slot.style.color = r.message.next_available_slot
            }
        }
        })
    }
})