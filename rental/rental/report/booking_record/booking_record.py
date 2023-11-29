# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from datetime import timedelta

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_room_booking_data(filters)
	frappe.msgprint(str(data))
	return columns, data

def get_columns(filters):
	columns = [{
		"fieldname" : "select_room_type",
		"label" : "Room Type",
		"fieldtype" : "Data",
		"width" : 150
		}]
	col_data =  ['12:00 am','12:30 am', '01:00 am', '01:30 am', '02:00 am', '02:30 am', '03:00 am', '03:30 am', '04:00 am', '04:30 am', '05:00 am', '05:30 am', '06:00 am', '06:30 am', '07:00 am', '07:30 am', '08:00 am', '08:30 am', '09:00 am', '09:30 am', '10:00 am', '10:30 am', '11:00 am', '11:30 am', 
				'12:00 pm', '12:30 pm', '01:00 pm', '01:30 pm', '02:00 pm', '02:30 pm', '03:00 pm', '03:30 pm','04:00 pm','04:30 pm','05:00 pm','05:30 pm','06:00 pm','06:30 pm','07:00 pm','07:30 pm','08:00 pm','08:30 pm','09:00 pm','09:30 pm','10:00 pm','10:30 pm','11:00 pm','11:30 pm']

	for row in col_data:
		columns.append({
			"fieldname" : row,
			"label" : row,
			"fieldtype" : "Data",
			"width" : 100
		})
	return columns

def get_room_booking_data(filters):

	
	start_date = str(filters.get('from_date'))
	end_date = str(filters.get('end_date'))

	dates = get_dates_between(start_date , end_date)
	final_data = []
	for row in dates:
		booking ={}
		data = frappe.db.sql(f""" SELECT name , customer , from_date , end_date , from_time , end_time , 
								select_room_type , status
								From `tabRoom Booking`  
								where from_date <= '{row}' <= end_date """ , as_dict = 1)

		final_data.append({'select_room_type' : str(row)})
		
		for i , d in enumerate(data):
			if d.status == "Active":
				booking.update({
					"select_room_type": d.select_room_type,
					d.from_time : "Booked",
					d.end_time : "Booked"
				})
				final_data.append(booking)

	return  final_data


def get_dates_between(start_date, end_date):
    return [getdate(start_date) + timedelta(days=i) 
            for i in range((getdate(end_date) - getdate(start_date)).days + 1)]