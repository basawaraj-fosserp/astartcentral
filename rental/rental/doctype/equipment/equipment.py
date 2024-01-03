# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Equipment(Document):
	pass

@frappe.whitelist()
def create_serial_no(equipment , serial_no):
	doc = frappe.new_doc("Equipment Serial No")
	doc.serial_no = serial_no
	doc.equipment = equipment
	doc.save(ignore_permissions = 1)
	return doc.name
