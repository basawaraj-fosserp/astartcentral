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
        if self.stock_entry:
            doc = frappe.get_doc("Stock Entry" , self.stock_entry)
            doc.cancel()

    def validate(self):
        from_date_obj = datetime.strptime(str(self.from_date), "%Y-%m-%d")
        to_date_obj   = datetime.strptime(str(self.to_date),   "%Y-%m-%d")
        if from_date_obj.weekday() >= 5:
            frappe.throw("Bookings are only allowed on weekdays (Monday – Friday).<br>Please select a valid <b>From Date</b>.")
        if to_date_obj.weekday() >= 5:
            frappe.throw("Bookings are only allowed on weekdays (Monday – Friday).<br>Please select a valid <b>To Date</b>.")
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
        self.validate_advance_booking_window()
        self.check_if_available()

    def validate_advance_booking_window(self):
        from frappe.utils import getdate, today
        booking_date = getdate(self.from_date)
        current_date = getdate(today())
        max_advance_date = current_date + timedelta(weeks=12)

        if booking_date > max_advance_date:
            frappe.throw(
                f"Oops! Equipment can only be booked up to <b>12 weeks</b> in advance.<br>"
                f"Please choose a date on or before <b>{max_advance_date.strftime('%B %d, %Y')}</b>."
            )

    def check_if_available(self):
        data = frappe.db.sql("""
            SELECT name, from_datetime, to_datetime, from_date, to_date, from_time, to_time
            FROM `tabEquipment Booking`
            WHERE docstatus = 1 AND status = 'Active'
              AND equipment = %s
              AND COALESCE(serial_no, '') = %s
              AND name != %s
        """, (self.equipment, self.serial_no or "", self.name or ""), as_dict=1)

        flag = 0
        error = "Equipment {0} is booked for below schedule. Please choose another time".format(self.equipment)
        error += """<br><br>
                <table width=100%>
                    <tr>
                        <td><b>From Time</b></td>
                        <td><b>To Time</b></td>
                    </tr>
                """
        for d in data:
            if d.get('from_datetime') <= self.from_datetime < d.get('to_datetime') or \
               d.get('from_datetime') < self.to_datetime <= d.get('to_datetime'):
                flag = 1
                error += """
                            <tr>
                                <td><p>{0} {1}</p></td>
                                <td><p>{2} {3}</p></td>
                            </tr>
                        """.format(d.get('from_date'), d.get('from_time'), d.get('to_date'), d.get('to_time'))
        if flag:
            error += "</table>"
            frappe.throw(error)

    def credit_utilization(self):
        time_diff = self.to_datetime - self.from_datetime
        time_diff_hour = time_diff.total_seconds()/3600
        from frappe.utils import now , getdate
        if not time_diff_hour:
            frappe.throw("From time and To time should not be same")
        now = now()
        current_time = now.split(" ")

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

        if from_time[1] == "PM" and from_time[0] not in ["12:00", "12:30"]:
            ad_from_datetime = ad_from_datetime + timedelta(hours=12)
        if end_time[1] == "PM" and end_time[0] not in ["12:00", "12:30"]:
            ad_to_datetime = ad_to_datetime + timedelta(hours=12)

        if not ((ad_from_datetime <= self.from_datetime <= ad_to_datetime) and (ad_from_datetime <= self.to_datetime <= ad_to_datetime)):
            frappe.throw(f"Booking is only allowed from {admin_from_time} to {admin_to_time}")

@frappe.whitelist()
def get_current_server_time(from_date=None):
    from frappe.utils import now_datetime, getdate
    current = now_datetime()
    is_today = getdate(from_date) == getdate(current.date()) if from_date else False
    return {
        "is_today": is_today,
        "current_minutes": current.hour * 60 + current.minute
    }

@frappe.whitelist()
def get_booked_slots(equipment, date, serial_no=None, exclude_name=None):
    """Return list of {from_time, to_time} for active bookings of this equipment on a given date."""
    data = frappe.db.sql("""
        SELECT from_time, to_time, from_datetime, to_datetime
        FROM `tabEquipment Booking`
        WHERE docstatus = 1 AND status = 'Active'
          AND equipment = %s
          AND COALESCE(serial_no, '') = %s
          AND (from_date = %s OR to_date = %s OR (from_date <= %s AND to_date >= %s))
          AND (%s IS NULL OR name != %s)
    """, (
        equipment,
        serial_no or "",
        date, date, date, date,
        exclude_name, exclude_name
    ), as_dict=1)

    return [{"from_time": d.from_time, "to_time": d.to_time,
             "from_datetime": str(d.from_datetime), "to_datetime": str(d.to_datetime)} for d in data]

@frappe.whitelist()
def get_booking_data(start, end, filters=None):
    """
    Fetch Equipment Booking calendar data within a date range.
    """
    if filters and isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (ValueError, TypeError):
            filters = {}
    else:
        filters = filters or {}

    from frappe.desk.calendar import get_event_conditions
    conditions = get_event_conditions("Equipment Booking", filters)

    data = frappe.db.sql(
        """
        SELECT
            eb.name,
            eb.from_datetime,
            eb.to_datetime,
            eb.title_of_reservation,
            eb.status,
            eb.equipment,
            eb.serial_no,
            eb.from_time,
            eb.to_time,
            eb.contact_name,
            eb.contact_number,
            equip.custom_color AS color
        FROM
            `tabEquipment Booking` AS eb
            LEFT JOIN `tabEquipment` AS equip
                ON equip.name = eb.equipment
        WHERE
            eb.docstatus = 1 AND (equip.status IS NULL OR equip.status != 'Inactive')
            AND eb.from_datetime <= %(end)s
            AND eb.to_datetime   >= %(start)s
            {conditions}
        ORDER BY
            eb.from_datetime ASC
        """.format(conditions=conditions),
        {"start": start, "end": end},
        as_dict=1,
    )

    for row in data:
        parts = [row.get("equipment") or "N/A"]
        if row.get("serial_no"):
            parts.append(f"SR: {row['serial_no']}")
        if row.get("contact_name"):
            parts.append(row["contact_name"])
        if row.get("contact_number"):
            parts.append(row["contact_number"])
        row["title"]  = " | ".join(parts)
        row["allDay"] = 0

    return data


def convert_inactive_equipment_booking():
    from frappe.utils import now
    to_datetime = now()
    data = frappe.db.sql(""" Select name from `tabEquipment Booking` where docstatus = 1 and status = "Active" and to_datetime < %s""", str(to_datetime), as_dict=1)

    for row in data:
        frappe.db.set_value("Equipment Booking" , row.get('name') , 'status' , 'Inactive',update_modified = False)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_equipment(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get("customer") if filters else None

    if customer:
        return frappe.db.sql(
            """
            SELECT ae.equipment
            FROM `tabAgreement on Equipment` ae
            INNER JOIN `tabEquipment` e ON e.name = ae.equipment
            WHERE ae.parent = %(customer)s
              AND (ae.equipment LIKE %(txt)s OR e.equipment_name LIKE %(txt)s)
            ORDER BY e.equipment_name ASC
            LIMIT %(start)s, %(page_len)s
            """,
            {
                "txt": f"%{txt}%",
                "customer": customer,
                "start": start,
                "page_len": page_len,
            },
        )

    return frappe.db.sql(
        """
        SELECT name
        FROM `tabEquipment`
        WHERE (name LIKE %(txt)s OR equipment_name LIKE %(txt)s)
        ORDER BY equipment_name ASC
        LIMIT %(start)s, %(page_len)s
        """,
        {
            "txt": f"%{txt}%",
            "start": start,
            "page_len": page_len,
        },
    )

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
