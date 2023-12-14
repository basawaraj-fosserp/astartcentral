# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.model.mapper import get_mapped_doc


class CreditRequest(Document):
	def on_submit(self):
		doc = frappe.new_doc("Material Request")
		doc.material_request_type = "Purchase"
		doc.customer = self.customer
		doc.schedule_date = getdate()
		doc.append("items",{
			"item_code":"Credit Points",
			"schedule_date":getdate(),
			"qty":self.credit,
			"warehouse":"{0} - {1}".format(self.customer , frappe.db.get_value("Company" , self.company , "abbr"))
		})
		doc.save()
		doc.submit()
		self.db_set("material_request" , doc.name)
		self.db_set("status" , "Pending")
	
	def on_cancel(self):
		doc = frappe.get_doc("Material Request" , self.material_request)
		doc.cancel()

@frappe.whitelist()
def create_credit_allocation(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Credit Request",
		source_name,
		{
			"Credit Request": {
				"doctype": "Credit Allocation",
				"field_map": {
					"credit" : "credit_score",
					"name" : "credit_request"
				},
				 "validation": {"docstatus": ["=", 1]}},
			
		},
		target_doc,
	)
	
	return doc