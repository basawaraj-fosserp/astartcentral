import frappe
from frappe.utils import now , getdate
from datetime import datetime , timedelta

@frappe.whitelist()
def current_room_booking_data(room):
    current_time = now()
    
    data = frappe.db.sql(f""" Select name , from_datetime , end_datetime , from_time , end_time , title_of_reservation
                                From `tabRoom Booking`
                                Where from_date = '{str(getdate())}'  and 
                                docstatus = 1 and select_room_type = '{room}' 
                                Order by from_datetime
                                 """, as_dict=True)

    now_time = datetime.strptime(str( current_time ), "%Y-%m-%d %H:%M:%S.%f")

    display_data = []
    current_booking = None
    for row in data:
        if now_time <= row.from_datetime:
            display_data.append(row)
        if row.from_datetime <= now_time <= row.end_datetime:
            current_booking = row
    current_date = datetime.now()
    formatted_date = current_date.strftime("%a,%d %B, %Y")
    display = {}
    event = None
    if display_data and not current_booking:
        event = str(display_data[0].get('from_time'))+" - "+str(display_data[0].get('end_time'))
        display.update({
            'title': display_data[0].get('title_of_reservation'),
            'event':event if event else "No Upcomming Event",
            'current_time' : str(datetime.now().time())[0:5] ,
            'today': formatted_date
        })
    elif display_data and current_booking:
        event = str(display_data[1].get('from_time'))+" - "+str(display_data[1].get('end_time'))
        display.update({
            'title': display_data[1].get('title_of_reservation'),
            'event' : event if event else "No Upcomming Event",
            'current_time' : str(datetime.now().time())[0:5],
            'today': formatted_date
        })


    display.update({
        'availability':"AVAILABLE",
        })
    if display_data:
        return display
    else:
        return {'event':event if event else "No Upcomming Event",'today': formatted_date ,
                 'availability':"AVAILABLE" , 'title' :'' , 'current_time' : str(datetime.now().time())[0:5],}