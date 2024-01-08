# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import now , getdate, today , flt
from datetime import datetime, timedelta, time

class RoomBooking(Document):
	def on_submit(self):
		if getdate(self.end_datetime) < getdate(self.from_datetime):
			frappe.throw("Please Select Correct Date<br>End Date can not be less than From Date")
		if self.from_date > now():
			self.status = "Active"
		self.credit_utilization()

	def on_cancel(self):
		from frappe.utils import now
		
		restricted_min = frappe.db.get_single_value("Admin Setting" , "minutes_before_cancellation")
		
		time_before_refund = self.from_datetime - timedelta(minutes=30)
		current_time = now()
		now = datetime.strptime(str( current_time ), "%Y-%m-%d %H:%M:%S.%f")
		
		if time_before_refund < now:
			frappe.throw(f"Cancellation is only allow before {restricted_min} minutes from booking time")
		
		doc = frappe.get_doc("Stock Entry" , self.stock_entry)
		doc.cancel()

	def validate(self):
		if not frappe.db.get_value("Room" , self.select_room_type , "enable_booking"):
			frappe.throw("The Room <b>{0}</b> is not allow to book".format(self.select_room_type))
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
			frappe.throw("Please Select Correct Date<br>End Date can not be less than From Date")
		current_time = datetime.strptime(str(now()) , "%Y-%m-%d %H:%M:%S.%f")
		if self.from_datetime > current_time:
			self.status = "Active"
		if self.from_datetime < current_time:
			frappe.throw("Only Future bookings are allow<br>Please select correct date and time")
		
		self.validate_admin_setting()
		self.check_if_available()
		self.check_admin_validation()

	def validate_admin_setting(self):
		# #To check Admin setting Refund validation
		admin_from_time = frappe.db.get_single_value("Admin Setting" ,  "booking_hours_from" )
		admin_to_time = frappe.db.get_single_value("Admin Setting" ,   "booking_hours_to")
		
		admin_time_obj = datetime.strptime(str(admin_from_time.split(' ')[0]), "%H:%M").time()
		admin_date_obj = datetime.strptime(str(self.from_date), "%Y-%m-%d")
		
		ad_from_datetime = datetime.combine(admin_date_obj.date(), admin_time_obj)

		admin_time_obj = datetime.strptime(str(admin_to_time.split(' ')[0]), "%H:%M").time()
		admin_date_obj = datetime.strptime(str(self.end_date), "%Y-%m-%d")
		
		ad_to_datetime = datetime.combine(admin_date_obj.date(), admin_time_obj)

		from_time = admin_from_time.split(' ')
		end_time = admin_to_time.split(' ')
		if from_time[1] == "PM":
			ad_from_datetime = ad_from_datetime + timedelta(hours = 12)
		if end_time[1] == "PM":
			ad_to_datetime = ad_to_datetime + timedelta(hours = 12)
		from_datetime = datetime.strptime(str(self.from_datetime) , "%Y-%m-%d %H:%M:%S")
		end_datetime = datetime.strptime(str(self.end_datetime) , "%Y-%m-%d %H:%M:%S")
		
		if not ((ad_from_datetime <= from_datetime <= ad_to_datetime) and (ad_from_datetime <= end_datetime <= ad_to_datetime)):
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
								<td width="10%">
									<b>SR No</b>
								</td>
								<td>
									<b>From Time</b>
								</td>
								<td>
									<b>To Time</b>
								</td>
							</tr>
					"""
			for i ,row in enumerate(booked_slot):
				error += f"<tr><td>{i+1}</td><td>{ frappe.format(row.from_datetime, {'fieldtype': 'Date'}) } {row.from_time}</td><td>{ frappe.format(row.end_datetime, {'fieldtype': 'Date'})} {row.end_time}</td></tr>"
			error += "</table>"
			error += "<br><p> Please Select another time or check with calendar </p>"
			frappe.throw(f"{self.select_room_type} is booked for the schedule below." + error)
	
	def credit_utilization(self):
		now = datetime.now()
		time_diff = self.end_datetime - self.from_datetime
		time_diff_hour = time_diff.total_seconds()/3600
		qty = time_diff_hour * frappe.db.get_value("Room" , self.select_room_type , "utilize_point")
		current_time = now.strftime("%H:%M:%S")

		doc = frappe.new_doc("Stock Entry")
		doc.company = self.company
		doc.posting_date = getdate()
		doc.posting_time = current_time
		doc.stock_entry_type = "Material Issue"
		abbr = frappe.db.get_value("Company" , self.company , 'abbr')
		doc.append("items",{
			"s_warehouse" : self.customer + " - {0}".format(abbr),
			"qty":qty,
			"item_code":"Credit Points"
		})
		doc.save(ignore_permissions = True)
		doc.submit()
		frappe.db.set_value("Room Booking" , self.name , "stock_entry" , doc.name)

	def check_admin_validation(self):
		disable_advance_booking_time = frappe.db.get_single_value("Admin Setting" , 'disable_advance_booking_time')
		dayofweeks = disable_advance_booking_time * 7
		get_last_date_of_booking = getdate(today()) - timedelta(days= -dayofweeks)
		if getdate(self.from_date) > getdate(get_last_date_of_booking):
			frappe.throw(f"Booking is only allow to the {frappe.format(get_last_date_of_booking , {'fieldtype': 'Date'})}")

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
			frappe.throw(f"Per day booking hour limit is {per_day_booking_hours}")

		if per_day_booking_hours < (flt(per_day_booking_hours) + flt(hours)) and (per_day_booking_hours-hours) < current_booking_hours:
			frappe.throw(f"Per day booking limit is {per_day_booking_hours} <br>Now you can only book for {flt(per_day_booking_hours) - flt(hours)} hour")

@frappe.whitelist()
def get_booking_data(start , end , filters = None):
	filters = json.loads(filters)
	
	conditions = ''
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Room Booking", filters)
	data = frappe.db.sql(f""" SELECT `tabRoom Booking`.name, `tabRoom Booking`.from_datetime, `tabRoom Booking`.end_datetime, `tabRoom Booking`.title_of_reservation, 
							`tabRoom Booking`.select_room_type, `tabRoom Booking`.status, `tabRoom Booking`.from_time, `tabRoom Booking`.end_time, room.color
							From `tabRoom Booking` 
							left join `tabRoom` as room ON room.name = `tabRoom Booking`.select_room_type
							where `tabRoom Booking`.docstatus = 1 {conditions}
							Order by `tabRoom Booking`.end_datetime """, as_dict = 1)
	
	for row in data:
		row.update({'title' : f"{row.select_room_type}"})
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
	if contact := frappe.db.exists("Contact" , {"user":user}):
		customer = frappe.db.sql(f""" Select name,link_name 
									From `tabDynamic Link` 
									where parent = "{contact}" and link_doctype ="Customer" """,as_dict = 1)
		
		
		return customer[0].link_name



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_rooms(doctype, txt, searchfield, start, page_len, filters):
	# filters = json.loads(filters)
	data = frappe.db.sql(f""" Select room
							From `tabAgreement on Room`
							Where parent = '{filters.get('customer')}' """)
	return data

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