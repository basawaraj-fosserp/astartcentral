# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import now, getdate
from datetime import datetime, timedelta

class EquipmentBooking(Document):
    def on_submit(self):
        if self.to_datetime < self.from_datetime:
            frappe.throw("Please Select Correct Date<br>End Date can not be less than From Date")
        if getdate(self.from_datetime) > getdate(now()):
            self.status = "Active"
        self.credit_utilization()

    def on_cancel(self):
        doc = frappe.get_doc("Stock Entry" , self.stock_entry)
        doc.cancel()

    def validate(self):
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

        time = self.to_time
        time_list = time.split(" ")

        

        end_time = time_list[0]
        end_date = str(self.to_date)

        if self.to_time == "12:00 AM":
            end_time = "00:00"
        if self.to_time == "12:30 AM":
            end_time = "00:30"

        time_obj = datetime.strptime(str(end_time), "%H:%M").time()
        date_obj = datetime.strptime(str(end_date), "%Y-%m-%d")

        combined_datetime = datetime.combine(date_obj.date(), time_obj)
        if time_list[1] == "PM" and time_list[0] not in ["12:00" , "12:30"]:
            combined_datetime = combined_datetime + timedelta(hours = 12)
        self.to_datetime =  combined_datetime

        if getdate(self.to_datetime) < getdate(self.from_datetime):
            frappe.throw("Please Select Correct Date<br>End Date can not be less than From Date")
        if getdate(self.from_datetime) > getdate(now()):
            self.status = "Active"
        if getdate(self.from_datetime) < getdate(now()):
            frappe.throw("Only Future bookings are allow<br>Please select correct date and time")
        self.validate_admin_setting()
        self.check_if_available()
        
                        
    def check_if_available(self):
        for row in self.equipment:
            data = frappe.db.sql(f""" SELECT eb.name, eb.from_datetime, eb.to_datetime, ei.quantity, eb.from_date, eb.to_date, eb.from_time, eb.to_time
                                From `tabEquipment Booking` as eb
                                Left Join `tabEquipment Items` as ei ON ei.parent = eb.name
                                Where
                                    eb.docstatus = 1 and eb.status="Active" and ei.equipment = "{row.equipment}" """,as_dict = 1)
            flag = 0
            error = "Equipment {0} is Booked for below schedule. Please choose another time".format(row.equipment)
            error += """<br><br>
                    <table width=100%>
                        <tr>
                            <td>
                                <b>From Time</b>
                            </td>
                            <td>
                                <b>To Time</b>
                            </td>
                        </tr>
                    """
            if len(data):
                for d in data:
                    if d.get('from_datetime') < (self.from_datetime) < (d.get('to_datetime')) or d.get('from_datetime') < (self.to_datetime) <table (d.get('to_datetime')):
                        flag = 1     
                        error += """
                                    <tr>
                                        <td>
                                            <p>{0} {1}</p>
                                        </td>
                                        <td>
                                            <p>{2} {3}</p>
                                        </td>
                                    </tr>
                                """.format(d.get('from_date'), d.get('from_time'), d.get('to_date'), d.get('to_time'))               
                if flag:
                    error += "</table>"
                    frappe.throw(error)
                
    
    def credit_utilization(self):
        now = datetime.now()
        time_diff = self.to_datetime - self.from_datetime
        time_diff_hour = time_diff.total_seconds()/3600
        current_time = now.strftime("%H:%M:%S")

        doc = frappe.new_doc("Stock Entry")
        doc.company = self.company
        doc.posting_date = getdate()
        doc.posting_time = current_time
        doc.stock_entry_type = "Material Issue"

        abbr = frappe.db.get_value("Company" , self.company , 'abbr')
        for row in self.equipment:
            qty = time_diff_hour * frappe.db.get_value("Equipment" , row.equipment , "rate_per_hour")
            doc.append("items",{
                "s_warehouse" : self.customer + " - {0}".format(abbr),
                "qty":qty,
                "item_code":"Credit Points"
            })

        doc.save(ignore_permissions = True)
        doc.submit()
        frappe.db.set_value("Equipment Booking" , self.name , "stock_entry" , doc.name)

    def validate_admin_setting(self):
        # #To check Admin setting Refund validation
        admin_from_time = frappe.db.get_single_value("Admin Setting" ,  "booking_hours_from" )
        admin_to_time = frappe.db.get_single_value("Admin Setting" ,   "booking_hours_to")
        
        admin_time_obj = datetime.strptime(str(admin_from_time.split(' ')[0]), "%H:%M").time()
        admin_date_obj = datetime.strptime(str(self.from_date), "%Y-%m-%d")
        
        ad_from_datetime = datetime.combine(admin_date_obj.date(), admin_time_obj)

        admin_time_obj = datetime.strptime(str(admin_to_time.split(' ')[0]), "%H:%M").time()
        admin_date_obj = datetime.strptime(str(self.to_date), "%Y-%m-%d")
        
        ad_to_datetime = datetime.combine(admin_date_obj.date(), admin_time_obj)

        from_time = admin_from_time.split(' ')
        end_time = admin_to_time.split(' ')

        if from_time[1] == "PM":
            ad_from_datetime = ad_from_datetime + timedelta(hours = 12)
        if end_time[1] == "PM":
            ad_to_datetime = ad_to_datetime + timedelta(hours = 12)

        if not ((ad_from_datetime <= self.from_datetime <= ad_to_datetime) and (ad_from_datetime <= self.to_datetime <= ad_to_datetime)):
            frappe.throw(f"Booking is only allowed from {admin_from_time} to {admin_to_time}")

@frappe.whitelist()
def get_booking_data(start , end , filters = None):
    filters = json.loads(filters)
    
    conditions = ''

    from frappe.desk.calendar import get_event_conditions

    conditions = get_event_conditions("Equipment Booking", filters)

    data = frappe.db.sql(f""" SELECT eb.name, eb.from_datetime, eb.to_datetime, eb.title_of_reservation, 
                            eb.status, et.equipment, eb.from_time , eb.to_time
                            From `tabEquipment Booking` as eb
                            left join `tabEquipment Items` as et ON et.parent = eb.name
                            where eb.docstatus = 1 {conditions}
                            Order by eb.to_datetime """, as_dict = 1)
    
    for row in data:
        row.update({'title' : f"{row.get('equipment')}" , "allDay": 0,})
    return data


def convert_inactive_booking():
    from frappe.utils import now
    to_datetime = now()
    data = frappe.db.sql(f""" Select name from `tabEquipment Booking` where docstatus = 1 and status = "Active" and to_datetime < '{str(to_datetime)}'""",as_dict = 1)
    
    for row in data:
        frappe.db.set_value("Room Booking" , row.get('name') , 'status' , 'Inactive',update_modified = False)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_equipment(doctype, txt, searchfield, start, page_len, filters):
    # filters = json.loads(filters)
    data = frappe.db.sql(f""" Select Equipment
                            From `tabAgreement on Equipment`
                            Where parent = '{filters.get('customer')}' """)
    return data