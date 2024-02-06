import frappe
from frappe.utils import now , getdate
from datetime import datetime , timedelta
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

    now_time = datetime.strptime(str( current_time ), "%Y-%m-%d %H:%M:%S.%f")

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
    display.update({'current_booking' : current_booking,
                    'current_time' : str(now_time.time())[0:5] ,
                    'today': formatted_date,
                    'event' : event if event else 'No Upcomming Event',
                    'availability':"NOT AVAILABLE" if current_booking else 'AVAILABLE',
                    })

    return display

@frappe.whitelist()
def get_color_code():
    doc = frappe.get_single('Display Color Settings')
    return doc

    