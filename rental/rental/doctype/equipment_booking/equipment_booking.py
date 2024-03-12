# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import now , getdate, today, flt, get_link_to_form
from datetime import datetime, timedelta

class EquipmentBooking(Document):
    def on_submit(self):
        if self.to_datetime < self.from_datetime:
            frappe.throw("Please select correct date.<br>End date can not be less than from date")
        from_datetime = datetime.strptime(str(self.from_datetime) , "%Y-%m-%d %H:%M:%S")
        from frappe.utils import now
        now = datetime.strptime(str(now()) , "%Y-%m-%d %H:%M:%S.%f")
        if from_datetime > now:
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

        from_datetime = datetime.strptime(str(self.from_datetime) , "%Y-%m-%d %H:%M:%S")
        to_datetime = datetime.strptime(str(self.to_datetime) , "%Y-%m-%d %H:%M:%S")
        if to_datetime < self.from_datetime:
            frappe.throw("Please select correct date<br>End date can not be less than from date")
        
        from frappe.utils import now

        now = datetime.strptime(now() , "%Y-%m-%d %H:%M:%S.%f")
        if from_datetime < now:
            frappe.throw("Only future bookings are allowed.<br>Kindly choose the accurate time and date.")
        self.validate_admin_setting()
        self.check_if_available()
        self.validate_for_multiple_serial_no()
        
    def validate_for_multiple_serial_no(self):
        unic_dict = {}
        for row in self.equipment:
            if not (unic_dict.get(row.equipment) == row.serial_no):
                unic_dict.update({row.equipment : row.serial_no})
            else:
                frappe.throw("""Serian No <b>{0}</b> not allow to select in multiple row.
                                <br><br>
                                <b>#{1} Row:</b> Please select another serial no""".format(row.serial_no , row.idx))
    def check_if_available(self):
        for row in self.equipment:
            data = frappe.db.sql(f""" SELECT eb.name, eb.from_datetime, eb.to_datetime, eb.from_date, eb.to_date, eb.from_time, eb.to_time
                                From `tabEquipment Booking` as eb
                                Left Join `tabEquipment Items` as ei ON ei.parent = eb.name
                                Where
                                    eb.docstatus = 1 and eb.status="Active" and ei.equipment = "{row.equipment}" """,as_dict = 1)
            flag = 0
            error = "Equipment {0} is booked for below schedule. Please choose another time".format(row.equipment)
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
                    if d.get('from_datetime') <= (self.from_datetime) < (d.get('to_datetime')) or d.get('from_datetime') < (self.to_datetime) <= (d.get('to_datetime')):
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
                    # frappe.throw(error)
                
    
    def credit_utilization(self):
        time_diff = self.to_datetime - self.from_datetime
        time_diff_hour = time_diff.total_seconds()/3600
        from frappe.utils import now , getdate
        if not time_diff_hour:
            frappe.throw("From time and To time should not be same")
        now = now()
        current_time = now.split(" ")

        doc = frappe.new_doc("Stock Entry")
        doc.company = self.company
        doc.posting_date = getdate()
        doc.posting_time = current_time[1]
        doc.stock_entry_type = "Material Issue"

        abbr = frappe.db.get_value("Company" , self.company , 'abbr')
        for row in self.equipment:
            if not frappe.db.get_value("Equipment" , row.equipment , "rate_per_hour"):
                from frappe.utils import now , getdate, today, flt, get_link_to_form
                frappe.throw(f"Please Update a Rate per hour in in equipment {get_link_to_form('Equipment',row.equipment)}")
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
                            eb.status, `tabEquipment Items`.equipment, eb.from_time , eb.to_time,`tabEquipment Items`.serial_no
                            From `tabEquipment Booking` as eb
                            left join `tabEquipment Items`  ON `tabEquipment Items`.parent = eb.name
                            where eb.docstatus = 1 {conditions}
                            Order by eb.to_datetime """, as_dict = 1)
    
    for row in data:
        row.update({'title' : f"{row.get('equipment')} SR={row.get('serial_no')}" , "allDay": 0})
    return data


def convert_inactive_equipment_booking():
    from frappe.utils import now
    to_datetime = now()
    data = frappe.db.sql(f""" Select name from `tabEquipment Booking` where docstatus = 1 and status = "Active" and to_datetime < '{str(to_datetime)}'""",as_dict = 1)
    
    for row in data:
        frappe.db.set_value("Equipment Booking" , row.get('name') , 'status' , 'Inactive',update_modified = False)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_equipment(doctype, txt, searchfield, start, page_len, filters):
    # filters = json.loads(filters)
    data = frappe.db.sql(f""" Select Equipment
                            From `tabAgreement on Equipment`
                            Where parent = '{filters.get('customer')}' """)
    return data

@frappe.whitelist()
def set_from_end_time(self):
	self = json.loads(self)
	if self.get('from_datetime') and self.get('to_datetime') and not(self.get('from_time') and self.get('to_time')):

		pm_start_time = str(getdate(self.get('from_datetime'))) +" "+"13:00:00"
		pm_start_time = datetime.strptime(str(pm_start_time) , "%Y-%m-%d %H:%M:00")

		from_datetime = datetime.strptime(str(self.get('from_datetime')) , "%Y-%m-%d %H:%M:%S")
		to_datetime = datetime.strptime(str(self.get('to_datetime')) , "%Y-%m-%d %H:%M:%S")

		row = {"from_date" : getdate(self.get('from_datetime')) , "to_date" : getdate(self.get('to_datetime'))}

		if pm_start_time <= from_datetime:
			from_datetime = from_datetime + timedelta(hours = -12)
			from_datetime = str(from_datetime).split(' ')
			from_datetime = from_datetime[1][0:-3]
			from_datetime = from_datetime + " " + "PM"
			row.update({"from_time":from_datetime})

		if pm_start_time <= to_datetime:
			to_datetime = to_datetime + timedelta(hours = -12)
			to_datetime = str(to_datetime).split(' ')
			to_datetime = to_datetime[1][0:-3]
			to_datetime = to_datetime + " " + "PM"
			row.update({"to_time":to_datetime})

		from_datetime = datetime.strptime(str(self.get('from_datetime')) , "%Y-%m-%d %H:%M:%S")
		to_datetime = datetime.strptime(str(self.get('to_datetime')) , "%Y-%m-%d %H:%M:%S")
		
		if pm_start_time > from_datetime:
			from_datetime = str(self.get('from_datetime')).split(' ')
			from_datetime = from_datetime[1][0:-3]
			from_datetime = from_datetime + " " + "AM"
			row.update({"from_time":from_datetime})
		if pm_start_time > to_datetime:
			to_datetime = str(self.get('to_datetime')).split(' ')
			to_datetime = to_datetime[1][0:-3]
			to_datetime = to_datetime + " " + "AM"
			row.update({"to_time":to_datetime })
            
		return row

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_available_serial_no(doctype, txt, searchfield, start, page_len, filters):
    serial_no = frappe.get_list("Serial No List", {"equipment" : filters.get('item')}, pluck = "serial_no" , ignore_permissions = "True")

    if not serial_no:
        return ()
    time = filters.get('from_time')
    time_list = time.split(" ")

    from_time = time_list[0]
    from_date = str(filters.get('from_date'))
    if filters.get('from_time') == "12:00 AM":
        from_time = "00:00"
    if filters.get('from_time') == "12:30 AM":
        from_time = "00:30"
    time_obj = datetime.strptime(str(from_time), "%H:%M").time()
    date_obj = datetime.strptime(str(from_date), "%Y-%m-%d")

    combined_datetime = datetime.combine(date_obj.date(), time_obj)
    if time_list[1] == "PM" and time_list[0] not in ["12:00" , "12:30"]:
        combined_datetime = combined_datetime + timedelta(hours = 12)
    from_datetime =  combined_datetime

    time = filters.get("to_time")
    time_list = time.split(" ")

    end_time = time_list[0]
    end_date = str(filters.get("to_date"))

    if filters.get("to_time") == "12:00 AM":
        end_time = "00:00"
    if filters.get("to_time") == "12:30 AM":
        end_time = "00:30"

    time_obj = datetime.strptime(str(end_time), "%H:%M").time()
    date_obj = datetime.strptime(str(end_date), "%Y-%m-%d")

    combined_datetime = datetime.combine(date_obj.date(), time_obj)
    if time_list[1] == "PM" and time_list[0] not in ["12:00" , "12:30"]:
        combined_datetime = combined_datetime + timedelta(hours = 12)
    to_datetime =  combined_datetime

    data = frappe.db.sql(f"""Select eq.name, eq.from_datetime, eq.to_datetime, ei.serial_no 
                            From `tabEquipment Booking` as eq
                            Left Join `tabEquipment Items` as ei On eq.name = ei.parent
                            Where eq.docstatus = 1 and ei.equipment = '{filters.get('item')}' and 
                            eq.status = "Active"
                            """,as_dict = 1)
    sr_list = []          
    if not data:
        for row in serial_no:
            sr_list.append((row , ""))
        return tuple(sr_list)
    
    under_use = []
    if data:
        for row in data:
            if (from_datetime <= (row.from_datetime) < to_datetime or 
                from_datetime < (row.to_datetime) <= to_datetime or 
                row.from_datetime <= (from_datetime) < row.to_datetime or 
                row.from_datetime < (to_datetime) <= row.to_datetime):
                under_use.append(row.serial_no)
    
        for row in serial_no:
            if row not in under_use:
                sr_list.append((row , ""))
        
        if not sr_list:
            return ()
        
        return tuple(sr_list)