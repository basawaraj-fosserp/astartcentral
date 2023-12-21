import frappe

def execute():
    if not frappe.db.exists("Item" , "Credit Points"):
        doc = frappe.new_doc("Item")
        doc.item_code = "Credit Points"
        doc.item_group = "Products"
        doc.is_stock_item = 1
        doc.valuation_rate = 1
        doc.save(ignore_permissions = True)