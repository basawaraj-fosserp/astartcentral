import frappe

def create_warehouse(self , method):
    if self.get("__islocal"):
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = self.name
        doc.save()