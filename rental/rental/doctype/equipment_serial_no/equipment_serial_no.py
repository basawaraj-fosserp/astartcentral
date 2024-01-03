# Copyright (c) 2024, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EquipmentSerialNo(Document):
	def on_trash(self):
		data = frappe.db.sql(f"Select name From `tabSerial No List` Where serial_no = '{self.name}' and 'equipment' ='{self.equipment}'  " , as_dict = 1)
		if data:
			for row in data:
				frappe.db.delete("Serial No List" , row.name)
