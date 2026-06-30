# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from rental.rental.utils import get_warehouse_for_customer

class CreditAllocation(Document):
	def on_submit(self):
		self.create_credit_allocation()
		if self.credit_request:
			frappe.db.set_value("Credit Request", self.credit_request, "status", "Allocated")

	def on_cancel(self):
		if self.credit_request:
			frappe.db.set_value("Credit Request", self.credit_request, "status", "Pending")
		doc = frappe.get_doc("Stock Entry", self.stock_entry)
		doc.cancel()

	def create_credit_allocation(self):
		warehouse = get_warehouse_for_customer(self.customer, self.company)
		doc = frappe.new_doc("Stock Entry")
		doc.posting_date = self.posting_date
		doc.posting_time = self.posting_time
		doc.stock_entry_type = "Material Receipt"
		doc.append("items", {
			"t_warehouse": warehouse,
			"qty": self.credit_score,
			"item_code": "Credit Points",
		})
		doc.save(ignore_permissions=True)
		doc.submit()
		frappe.db.set_value("Credit Allocation", self.name, "stock_entry", doc.name)
		
	