# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Equipment(Document):
	def validate(self):
		if not self.rate_per_hour:
			frappe.throw("Input mandatory field <b>Rate Per Hour</b>")

@frappe.whitelist()
def create_serial_no(equipment , serial_no):
	doc = frappe.new_doc("Equipment Serial No")
	doc.serial_no = serial_no
	doc.equipment = equipment
	doc.save(ignore_permissions = 1)

	doc= frappe.get_doc("Equipment" , equipment)
	doc.append('serial_no',{
		"equipment":equipment,
		'serial_no':serial_no
	})
	doc.save(ignore_permissions= True)
	doc.reload()
