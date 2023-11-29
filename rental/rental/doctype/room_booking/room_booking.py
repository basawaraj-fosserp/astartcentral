# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import now , getdate, today , flt
from datetime import datetime, timedelta

class RoomBooking(Document):
	def on_submit(self):
		if getdate(self.end_datetime) < getdate(self.from_datetime):
			frappe.throw("Please Select Correct Date<br>End Date can not be less than From Date")
		if self.from_date > now():
			self.status = "Active"

	def validate(self):
		time = self.from_time
		time_list = time.split(" ")

		from_time = time_list[0]
		from_date = str(self.from_date)
		if self.from_time == "12:00 am":
			from_time = "00:00"
		if self.from_time == "12:30 am":
			from_time = "00:30"
		time_obj = datetime.strptime(str(from_time), "%H:%M").time()
		date_obj = datetime.strptime(str(from_date), "%Y-%m-%d")

		combined_datetime = datetime.combine(date_obj.date(), time_obj)
		if time_list[1] == "pm":
			combined_datetime = combined_datetime + timedelta(hours = 12)
		self.from_datetime =  combined_datetime

		time = self.end_time
		time_list = time.split(" ")

		end_time = time_list[0]
		end_date = str(self.end_date)

		time_obj = datetime.strptime(str(end_time), "%H:%M").time()
		date_obj = datetime.strptime(str(end_date), "%Y-%m-%d")

		combined_datetime = datetime.combine(date_obj.date(), time_obj)
		if time_list[1] == "pm":
			combined_datetime = combined_datetime + timedelta(hours = 12)
		self.end_datetime =  combined_datetime
		if self.end_datetime < self.from_datetime:
			frappe.throw("Please Select Correct Date<br>End Date can not be less than From Date")
		if getdate(self.from_datetime) > getdate(now()):
			self.status = "Active"
		if getdate(self.from_datetime) < getdate(now()):
			frappe.throw("Only Future bookings are allow<br>Please select correct date and time")
		self.check_if_available()
		self.check_admin_validation()

	def check_if_available(self):
		data = frappe.db.sql(f"""Select name , from_datetime ,end_datetime 
								From `tabRoom Booking`
								where docstatus = 1 and select_room_type = '{self.select_room_type}' and status = 'Active' """,as_dict="true")
		booked_slot = []
		flag = False
		if data:
			for row in data:
				if row.get('from_datetime') <= (self.from_datetime) <= (row.get('end_datetime')) or row.get('from_datetime') <= (self.end_datetime) <= (row.get('end_datetime')):
					flag = True
		if flag:
			booked_slot = frappe.db.sql(f"""Select name , from_datetime ,end_datetime , from_time , end_time
								From `tabRoom Booking`
								where docstatus = 1 and select_room_type = '{self.select_room_type}' and status = 'Active' """,as_dict="true")
			error = """<table border=1 width="100%">
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
			frappe.throw(f"{self.select_room_type} is booked for this bellow schedule" + error)
	
	
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
									and select_room_type = '{self.select_room_type}' and customer = '{self.customer}' """,as_dict = 1)
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
			frappe.throw(f"Per day booking limit is {per_day_booking_hours} <br>Now you can only book for {flt(per_day_booking_hours) - flt(hours)} ")

		# hours = 0

		# for row in data:
		# 	difference = row.end_datetime - row.from_datetime
		# 	booking_hours = difference.total_seconds()/3600
		# 	hours += booking_hours

		# if hours > per_day_booking_hours:
		# 	frappe.throw(f"Room {self.select_room_type} is not available for today")




@frappe.whitelist()
def get_booking_data(start , end , filters = None):
	filters = json.loads(filters)
	
	conditions = ''
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Room Booking", filters)
	data = frappe.db.sql(f""" SELECT name, from_datetime, end_datetime, title_of_reservation ,select_room_type , status
							From `tabRoom Booking`  
							where docstatus = 1 {conditions}
							Order by end_datetime """, as_dict = 1)
	
	for row in data:
		row.update({'title' : f"<br>{ frappe.format(row.get('from_datetime'), {'fieldtype': 'Datetime'}) } To { frappe.format(row.get('end_datetime'), {'fieldtype': 'Datetime'}) }"})
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
	if customer := frappe.db.exists("Customer" , {"user":user}):
		return customer
