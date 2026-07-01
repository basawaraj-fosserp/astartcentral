# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import now , getdate, today, flt, get_link_to_form, get_datetime
from datetime import datetime, timedelta, time

class RoomBooking(Document):
    def on_submit(self):
        from frappe.utils import now
        from_datetime = datetime.strptime(str(self.from_datetime) , "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(str(self.end_datetime) , "%Y-%m-%d %H:%M:%S")
        if end_datetime < from_datetime:
            frappe.throw("Please select correct date.<br>End date can not be less than from date.")
        self.db_set('booking_time' , now())
        now = datetime.strptime(now() , "%Y-%m-%d %H:%M:%S.%f")
        if from_datetime > now:
            self.status = "Active"
        self.credit_utilization()

    def on_cancel(self):
        from frappe.utils import now, get_datetime

        if get_datetime(self.from_datetime) < get_datetime(now()):
            frappe.throw(f"Cancellation not allowed after the booking time <b>{self.from_datetime}</b>")

        restricted_min = frappe.db.get_single_value("Admin Setting", "minutes_before_cancellation")
        
        if restricted_min:  # Guard against None
            time_before_refund = get_datetime(self.from_datetime) + timedelta(minutes=-restricted_min)
            if get_datetime(time_before_refund) < get_datetime(now()) < get_datetime(self.from_datetime):
                frappe.throw(f"Cancellation should not be allowed within {restricted_min} min")

        doc = frappe.get_doc("Stock Entry", self.stock_entry)
        doc.cancel()

    def validate(self):
        from frappe.utils import now , getdate
        if not frappe.db.get_value("Room" , self.select_room_type , "enable_booking"):
            frappe.throw("The Room <b>{0}</b> is not allow to book".format(self.select_room_type))
        from_date_obj = datetime.strptime(str(self.from_date), "%Y-%m-%d")
        end_date_obj  = datetime.strptime(str(self.end_date),  "%Y-%m-%d")
        if from_date_obj.weekday() >= 5:
            frappe.throw("Bookings are only allowed on weekdays (Monday – Friday).<br>Please select a valid <b>From Date</b>.")
        if end_date_obj.weekday() >= 5:
            frappe.throw("Bookings are only allowed on weekdays (Monday – Friday).<br>Please select a valid <b>End Date</b>.")
        time = self.from_time
        time_list = time.split(" ")

        from_time = time_list[0]
        from_date = str(self.from_date)
        if self.from_time == "12:00 AM":
            from_time = "00:00"
        if self.from_time == "12:30 AM":
            from_time = "00:30"

        time_obj = datetime.strptime(str(from_time), "%H:%M").time()
        date_obj = datetime.strptime(str(from_date), "%Y-%m-%d")

        combined_datetime = datetime.combine(date_obj.date(), time_obj)
        if time_list[1] == "PM" and time_list[0] not in ["12:00" , "12:30"]:
            combined_datetime = combined_datetime + timedelta(hours = 12)
        self.from_datetime =  combined_datetime

        time = self.end_time
        time_list = time.split(" ")

        end_time = time_list[0]
        end_date = str(self.end_date)

        time_obj = datetime.strptime(str(end_time), "%H:%M").time()
        date_obj = datetime.strptime(str(end_date), "%Y-%m-%d")

        combined_datetime = datetime.combine(date_obj.date(), time_obj)
        if time_list[1] == "PM" and self.end_time not in ["12:00 PM", "12:30 PM"]:
            combined_datetime = combined_datetime + timedelta(hours = 12)
        self.end_datetime =  combined_datetime
        if self.end_datetime < self.from_datetime:
            frappe.throw("Please select correct date.<br>End date can not be less than from date")
        current_time = datetime.strptime(now() , "%Y-%m-%d %H:%M:%S.%f")
        if self.from_datetime > current_time:
            self.status = "Active"
        if self.from_datetime < current_time:
            frappe.throw("Only future bookings are allowed.<br>Kindly choose the accurate time and date.")
        
        self.validate_current_month_booking()
        self.validate_admin_setting()
        self.check_if_available()
        self.check_admin_validation()
        self.same_time_booking_validation()
    
    def validate_current_month_booking(self):
        from frappe.utils import getdate, today
        booking_date = getdate(self.from_date)
        current_date = getdate(today())

        if booking_date.month != current_date.month or booking_date.year != current_date.year:
            import calendar
            current_month_name = current_date.strftime("%B %Y")
            booking_month_name = booking_date.strftime("%B %Y")
            frappe.throw(
                f"Oops! It looks like the selected date is in <b>{booking_month_name}</b>.<br>"
                f"Your credits are available for <b>{current_month_name}</b> only.<br>"
                f"Please choose a date within the current month to proceed."
            )

    def same_time_booking_validation(self):
        todays_data = frappe.db.sql(f"""
                    Select name, from_date, from_datetime, from_time, customer, end_datetime, end_date, end_time, select_room_type
                    From `tabRoom Booking` as rb
                    Where docstatus = 1 and customer = '{self.customer}' and from_date = '{self.from_date}'
        """, as_dict=1)

        for row in todays_data:
            if get_datetime(self.from_datetime) < get_datetime(row.end_datetime) and \
               get_datetime(self.end_datetime) > get_datetime(row.from_datetime):
                frappe.throw(
                    f"Customer <b>{self.customer}</b> already has a booking for room "
                    f"<b>{row.select_room_type}</b> from <b>{row.from_time}</b> to "
                    f"<b>{row.end_time}</b> on this date.<br>"
                    f"Simultaneous room bookings are not allowed. Please choose a different time."
                )


    def validate_admin_setting(self):
        # System Manager and Astart Admin bypass the booking hours restriction
        if any(role in frappe.get_roles() for role in ["System Manager", "Astart Admin"]):
            return

        admin_from_time = frappe.db.get_single_value("Admin Setting", "booking_hours_from")
        admin_to_time   = frappe.db.get_single_value("Admin Setting", "booking_hours_to")

        if not admin_from_time or not admin_to_time:
            return

        def parse_admin_time(time_str, date_str):
            parts = time_str.split(' ')
            t = datetime.strptime(parts[0], "%H:%M").time()
            dt = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), t)
            if parts[1] == "PM" and parts[0] not in ["12:00", "12:30"]:
                dt += timedelta(hours=12)
            return dt

        ad_from_datetime = parse_admin_time(admin_from_time, str(self.from_date))
        ad_to_datetime   = parse_admin_time(admin_to_time,   str(self.end_date))

        from_datetime = datetime.strptime(str(self.from_datetime), "%Y-%m-%d %H:%M:%S")
        end_datetime  = datetime.strptime(str(self.end_datetime),  "%Y-%m-%d %H:%M:%S")

        if not (ad_from_datetime <= from_datetime and end_datetime <= ad_to_datetime):
            frappe.throw(f"Booking is only allowed from {admin_from_time} to {admin_to_time}")


    def after_insert(self):
        if self.from_web_form:
            self.submit()

    def check_if_available(self):
        data = frappe.db.sql(f"""Select name , from_datetime ,end_datetime 
                                From `tabRoom Booking`
                                where docstatus = 1 and select_room_type = '{self.select_room_type}' and status = 'Active' """,as_dict="true")
        booked_slot = []
        flag = False
        if data:
            for row in data:
                if row.get('from_datetime') <= (self.from_datetime) < (row.get('end_datetime')) or row.get('from_datetime') < (self.end_datetime) < (row.get('end_datetime')):
                    flag = True
        if flag:
            booked_slot = frappe.db.sql(f"""Select name , from_datetime ,end_datetime , from_time , end_time
                                From `tabRoom Booking`
                                where docstatus = 1 and select_room_type = '{self.select_room_type}' and status = 'Active' """,as_dict="true")
            error = """<br><table border=1 width="100%">
                            <tr>
                                <td width="10%" align="center">
                                    <b>SR No</b>
                                </td>
                                <td align="center">
                                    <b>From Time</b>
                                </td>
                                <td align="center">
                                    <b>To Time</b>
                                </td>
                            </tr>
                    """
            for i ,row in enumerate(booked_slot):
                error += f"<tr><td align='center'>{i+1}</td><td align='center'>{ frappe.format(row.from_datetime, {'fieldtype': 'Date'}) }, {row.from_time}</td><td align='center'>{ frappe.format(row.end_datetime, {'fieldtype': 'Date'})}, {row.end_time}</td></tr>"
            error += "</table>"
            error += "<br><p> Please select another time or check the calendar.</p>"
            frappe.throw(f"{self.select_room_type} is booked for the schedule below." + error)
    
    def credit_utilization(self):
        time_diff = self.end_datetime - self.from_datetime
        time_diff_hour = time_diff.total_seconds()/3600
        if not time_diff_hour:
            frappe.throw("From time and End time should not be same")
        if not frappe.db.get_value("Room" , self.select_room_type , "utilize_point"):
            from frappe.utils import now , getdate, today, flt, get_link_to_form
            frappe.throw(f"Please Update a Rate per hour in in room {get_link_to_form('Room',self.select_room_type)}")
        qty = time_diff_hour * frappe.db.get_value("Room" , self.select_room_type , "utilize_point")
        
        from frappe.utils import now , getdate
        now = now()
        
        current_time = now.split(" ")

        from rental.rental.utils import get_warehouse_for_customer
        warehouse = get_warehouse_for_customer(self.customer, self.company)
        doc = frappe.new_doc("Stock Entry")
        doc.company = self.company
        doc.posting_date = getdate()
        doc.posting_time = current_time[1]
        doc.stock_entry_type = "Material Issue"
        doc.append("items", {
            "s_warehouse": warehouse,
            "qty": qty,
            "item_code": "Credit Points",
        })
        doc.save(ignore_permissions = True)
        doc.submit()
        frappe.db.set_value("Room Booking" , self.name , "stock_entry" , doc.name)

    def check_admin_validation(self):
        # System Manager and Astart Admin bypass all booking restrictions
        if any(role in frappe.get_roles() for role in ["System Manager", "Astart Admin"]):
            return

        disable_advance_booking_time = frappe.db.get_single_value("Admin Setting" , 'disable_advance_booking_time')
        dayofweeks = disable_advance_booking_time * 7
        get_last_date_of_booking = getdate(today()) - timedelta(days= -dayofweeks)
        if getdate(self.from_date) > getdate(get_last_date_of_booking):
            frappe.throw(f"Booking is only allow till {frappe.format(get_last_date_of_booking , {'fieldtype': 'Date'})}")

        difference = self.end_datetime - self.from_datetime
        booking_hours = difference.total_seconds()/3600
        default_booking_hours = frappe.db.get_single_value("Admin Setting" , "max_booking_hours_per_room_booking")
        if booking_hours > default_booking_hours:
            frappe.throw(f"Maximum booking allow for {default_booking_hours} hours")

        #Max hours per day per room
        data =  frappe.db.sql(f""" SELECT name , from_datetime , end_datetime
                                    From `tabRoom Booking` 
                                    where docstatus = 1 and status = "Active" and from_date = '{self.from_date}'
                                    and select_room_type = '{self.select_room_type}' and customer = '{self.customer}'
                                    Order By from_datetime """,as_dict = 1)
        hours = 0
        if data:
            for row in data:
                difference = row.end_datetime - row.from_datetime
                booking_hours = difference.total_seconds()/3600
                hours += booking_hours
        
        per_day_booking_hours = frappe.db.get_single_value("Admin Setting" , "max_hours_per_day_per_room")
        
        difference = self.end_datetime - self.from_datetime
        current_booking_hours = difference.total_seconds()/3600

        if per_day_booking_hours <= hours:
            frappe.throw(f"The Per-day booking hour limit is {per_day_booking_hours}")

        if per_day_booking_hours < (flt(per_day_booking_hours) + flt(hours)) and (per_day_booking_hours-hours) < current_booking_hours:
            frappe.throw(f"The per-day booking limit is {per_day_booking_hours} hours.<br>you can book for {flt(per_day_booking_hours) - flt(hours)} hour more.")

@frappe.whitelist()
def get_booking_data(start , end , filters = None):
    filters = json.loads(filters)
    
    conditions = ''
    from frappe.desk.calendar import get_event_conditions
    conditions = get_event_conditions("Room Booking", filters)
    data = frappe.db.sql(f""" SELECT `tabRoom Booking`.name,
                            `tabRoom Booking`.from_datetime,
                            `tabRoom Booking`.end_datetime,
                            `tabRoom Booking`.title_of_reservation,
                            `tabRoom Booking`.select_room_type,
                            `tabRoom Booking`.status,
                            `tabRoom Booking`.from_time,
                            `tabRoom Booking`.end_time,
                            `tabRoom Booking`.contact_name,
                            `tabRoom Booking`.contact_number,
                            room.color
                            From `tabRoom Booking`
                            left join `tabRoom` as room ON room.name = `tabRoom Booking`.select_room_type
                            where `tabRoom Booking`.docstatus = 1 and `tabRoom Booking`.status != 'Inactive' {conditions}
                            Order by `tabRoom Booking`.end_datetime """, as_dict=1)

    for row in data:
        parts = [row.select_room_type]
        if row.contact_name:
            parts.append(row.contact_name)
        if row.contact_number:
            parts.append(row.contact_number)
        row.update({'title': ' | '.join(parts)})
    return data

#cron job function
def convert_inactive_booking():
    from frappe.utils import now
    end_datetime = now()
    data = frappe.db.sql(f""" Select name from `tabRoom Booking` where docstatus = 1 and status = "Active" and end_datetime < '{str(end_datetime)}'""",as_dict = 1)
    
    for row in data:
        frappe.db.set_value("Room Booking" , row.get('name') , 'status' , 'Inactive',update_modified = False)

@frappe.whitelist(allow_guest = True)
def check_log_in_user(user):
    if "Astart Admin" not in frappe.get_roles():
        if contact := frappe.db.exists("Contact" , {"user":user}):
            customer = frappe.db.sql(f""" Select name,link_name 
                                        From `tabDynamic Link` 
                                        where parent = "{contact}" and link_doctype ="Customer" """,as_dict = 1)
            
            if not len(customer):
                frappe.throw("Please Contact to Admin, your contact document is not link with your user")
            
            return customer[0].link_name



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_rooms(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer") if filters else None
    conditions = ""
    if customer:
        conditions = "AND aor.parent = %(customer)s"

    return frappe.db.sql(
        """
        SELECT aor.room, r.description
        FROM `tabAgreement on Room` aor
        INNER JOIN `tabRoom` r ON r.name = aor.room
        WHERE (aor.room LIKE %(txt)s OR r.room_name LIKE %(txt)s)
        {conditions}
        LIMIT %(start)s, %(page_len)s
        """.format(conditions=conditions),
        {
            "txt": f"%{txt}%",
            "customer": customer,
            "start": start,
            "page_len": page_len,
        },
    )

@frappe.whitelist()
def get_time_picker_data(room, date):
    admin_from = frappe.db.get_single_value("Admin Setting", "booking_hours_from")
    admin_to   = frappe.db.get_single_value("Admin Setting", "booking_hours_to")

    booked = frappe.db.sql("""
        SELECT from_time, end_time
        FROM `tabRoom Booking`
        WHERE docstatus = 1
          AND status = 'Active'
          AND select_room_type = %(room)s
          AND from_date = %(date)s
    """, {"room": room, "date": date}, as_dict=True)

    max_booking_hours = frappe.db.get_single_value("Admin Setting", "max_booking_hours_per_room_booking")

    from frappe.utils import now_datetime, getdate, convert_utc_to_user_timezone
    current = convert_utc_to_user_timezone(now_datetime())
    booking_date = getdate(date)
    return {
        "admin_from": admin_from,
        "admin_to": admin_to,
        "booked_slots": booked,
        "is_today": booking_date == getdate(current.date()),
        "current_minutes": current.hour * 60 + current.minute,
        "max_booking_hours": max_booking_hours or 0
    }

@frappe.whitelist()
def get_current_time():
    from frappe.utils import now_datetime, today, convert_utc_to_user_timezone
    current = convert_utc_to_user_timezone(now_datetime())
    admin_from = frappe.db.get_single_value("Admin Setting", "booking_hours_from")
    admin_to   = frappe.db.get_single_value("Admin Setting", "booking_hours_to")
    return {
        "today": str(current.date()),
        "hours": current.hour,
        "minutes": current.minute,
        "admin_from": admin_from,
        "admin_to": admin_to
    }

@frappe.whitelist()
def set_from_end_time(self):
    self = json.loads(self)
    if self.get('from_datetime') and self.get('end_datetime') and not(self.get('from_time') and self.get('end_time')):

        pm_start_time = str(getdate(self.get('from_datetime'))) +" "+"13:00:00"
        pm_start_time = datetime.strptime(str(pm_start_time) , "%Y-%m-%d %H:%M:00")

        from_datetime = datetime.strptime(str(self.get('from_datetime')) , "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(str(self.get('end_datetime')) , "%Y-%m-%d %H:%M:%S")

        row = {"from_date" : getdate(self.get('from_datetime')) , "end_date" : getdate(self.get('end_datetime'))}

        if pm_start_time <= from_datetime:
            from_datetime = from_datetime + timedelta(hours = -12)
            from_datetime = str(from_datetime).split(' ')
            from_datetime = from_datetime[1][0:-3]
            from_datetime = from_datetime + " " + "PM"
            row.update({"from_time":from_datetime})

        if pm_start_time <= end_datetime:
            end_datetime = end_datetime + timedelta(hours = -12)
            end_datetime = str(end_datetime).split(' ')
            end_datetime = end_datetime[1][0:-3]
            end_datetime = end_datetime + " " + "PM"
            row.update({"end_time":end_datetime})

        from_datetime = datetime.strptime(str(self.get('from_datetime')) , "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(str(self.get('end_datetime')) , "%Y-%m-%d %H:%M:%S")
        
        if pm_start_time > from_datetime:
            from_datetime = str(self.get('from_datetime')).split(' ')
            from_datetime = from_datetime[1][0:-3]
            from_datetime = from_datetime + " " + "AM"
            row.update({"from_time":from_datetime})
        if pm_start_time > end_datetime:
            end_datetime = str(self.get('end_datetime')).split(' ')
            end_datetime = end_datetime[1][0:-3]
            end_datetime = end_datetime + " " + "AM"
            row.update({"end_time":end_datetime })

        return row	


