import frappe
from frappe.utils import now, getdate, get_datetime, get_time
import json
@frappe.whitelist()
def current_room_booking_data(room):
    current_time = now()
    
    data = frappe.db.sql(f""" Select name, 
                                    from_datetime, 
                                    end_datetime, 
                                    from_time, 
                                    end_time, 
                                    title_of_reservation,
                                    contact_name
                                From `tabRoom Booking`
                                Where from_date = '{str(getdate())}'  and 
                                docstatus = 1 and select_room_type = '{room}' 
                                Order by from_datetime
                                 """, as_dict=True)

    now_time = get_datetime(current_time)

    display_data = []
    current_booking = None
    for row in data:
        if row.from_datetime <= now_time <= row.end_datetime:
            current_booking = row
        elif now_time <= row.from_datetime:
            display_data.append(row)
    current_date = getdate(now())
    formatted_date = current_date.strftime("%a,%d %b, %Y")
    display = {}
    event = []
    if len(display_data) >= 1:
        event = display_data

    next_available_slot = None
    if current_booking:
        next_available_slot = current_booking.end_time
        last_end = current_booking.end_datetime
        for row in display_data:
            if row.from_datetime <= last_end:
                next_available_slot = row.end_time
                last_end = row.end_datetime
            else:
                break

        booking_hours_to = frappe.db.get_single_value("Admin Setting", "booking_hours_to")
        if booking_hours_to and get_time(next_available_slot) >= get_time(booking_hours_to):
            next_available_slot = None

    display.update({'current_booking' : current_booking,
                    'current_time' : str(now_time.time())[0:5] ,
                    'today': formatted_date,
                    'event' : event if event else 'No Upcoming Event',
                    'availability':"OCCUPIED" if current_booking else 'AVAILABLE',
                    'next_available_slot' : next_available_slot,
                    })

    return display

@frappe.whitelist()
def get_color_code():
    doc = frappe.get_single('Display Color Settings')
    return doc

    