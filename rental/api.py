import frappe
from frappe import _
from erpnext.stock.stock_ledger import  get_previous_sle , NegativeStockError
from frappe.utils import flt, getdate, now  
from frappe.model.mapper import get_mapped_doc
from datetime import datetime, timedelta, time


def create_warehouse(self , method):
    if self.get("__islocal"):
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = self.name
        doc.save(ignore_permissions = True)
        
def on_update(self , method):
    data = frappe.db.get_list("Credit Allocation" , filters ={'customer':self.name , "docstatus":1})
    if self.custom_credit_assigned_monthly and not len(data):
        doc_ = frappe.new_doc("Credit Allocation")
        doc_.customer = self.name
        doc_.ignore_linked_doctypes= ['Customer']
        doc_.posting_date = getdate()
        doc_.credit_score = self.custom_credit_assigned_monthly
        doc_.save(ignore_permissions = True)
        doc_.submit()

def set_actual_qty(self):
    from erpnext.stock.stock_ledger import is_negative_stock_allowed

    for d in self.get("items"):
        allow_negative_stock = is_negative_stock_allowed(item_code=d.item_code)
        previous_sle = get_previous_sle(
            {
                "item_code": d.item_code,
                "warehouse": d.s_warehouse or d.t_warehouse,
                "posting_date": self.posting_date,
                "posting_time": self.posting_time,
            }
        )

        # get actual stock at source warehouse
        d.actual_qty = previous_sle.get("qty_after_transaction") or 0

        # validate qty during submit
        if (
            d.docstatus == 1
            and d.s_warehouse
            and not allow_negative_stock
            and flt(d.actual_qty, d.precision("actual_qty"))
            < flt(d.transfer_qty, d.precision("actual_qty"))
        ):
            frappe.throw(
                _(
                    "Insufficient Credit Balance"
                )
                + "<br><br>"
                + _("Available Balance is {0}, you need {1}").format(
                    frappe.bold(flt(d.actual_qty, d.precision("actual_qty"))), frappe.bold(d.transfer_qty)
                ),
                NegativeStockError,
                title=_("Insufficient Balance"),
            )


@frappe.whitelist()
def check_roles():
    if "System Manager" in frappe.get_roles():
        return True
    return False

@frappe.whitelist()
def get_current_credit():
    customer = frappe.db.sql(f""" Select dl.link_name
                                From `tabDynamic Link` as dl
                                left join `tabContact` as co  ON co.name = dl.parent
                                Where dl.parenttype ='Contact' and co.user = '{frappe.session.user}' and
                                dl.link_doctype = 'Customer' """,as_dict = 1)

    if not len(customer):
        return  { "value" : 0 , "fieldtype":"Float"}

    warehouse = "{0} - {1}".format(customer[0].link_name , frappe.db.get_value("Company","Kingstech Pvt Ltd","abbr"))
    data = frappe.db.sql(f""" Select qty_after_transaction From `tabStock Ledger Entry`
                            where is_cancelled = 0 and warehouse = "{warehouse}" and item_code ="Credit Points" 
                            Order By creation Desc """,as_dict = 1)
    if data:
        return { "value" : data[0].qty_after_transaction , "fieldtype":"Float"}
        
    return  { "value" : 0 , "fieldtype":"Float"}

@frappe.whitelist()
def create_subscription(source_name , target_doc = None):
    doclist = get_mapped_doc(
		"Customer",
		source_name,
		{
			"Customer": {
                "doctype": "Subscription",
                "field_map": {
					"doctype":"party_type",
                    "name":"party"
				},
                },
			
		},
		target_doc,
	)
    return doclist


def check_subscription_period():
    customer = []
    doc_list = frappe.get_list("Subscription" , pluck = "name")
    for row in doc_list:
        doc = frappe.get_doc("Subscription" , row)
        if getdate(doc.end_date) < getdate():
            customer.append(doc.customer)
    if customer:
        for row in customer:
            users = frappe.db.sql(f""" Select user
                                    From `tabContact` as c
                                    left join `tabDynamic Link` as dl On dl.parent = c.name
                                    Where dl.link_doctype = "Customer" and dl.name = '{row}' """,as_dict = 1)
            user = users[0].user
            frappe.db.set_value("User" , user , "enable" , 0)
        

def create_item_from_equipment(self , method):
    if frappe.db.exists("Item" , self.name):
        return
    doc = frappe.new_doc("Item")
    doc.item_code = self.name
    doc.valuation_rate = 1
    doc.has_serial_no = 1
    doc.item_group = "All Item Groups"
    doc.stock_uom = "Nos"
    doc.is_stock_item = 1
    doc.save()

# on submit of subscription allocate a credit point
# def allocation_of_credit_bases_payment(self ,method):
#     paid_amount = self.paid_amount
#     data = []
#     for row in self.references:
#         if row.reference_doctype == "Sales Invoice" and self.payment_type == "Receive":
#             data = frappe.db.sql(f""" Select spd.plan , spd.qty
#                                     From `tabSubscription Invoice` as si
#                                     left join `tabSubscription` as su On su.name = si.parent
#                                     left join `tabSubscription Plan Detail` as spd on spd.parent = su.name
#                                     Where document_type = "Sales Invoice" and invoice = '{row.reference_name}'
#                                     """,as_dict = 1)

#             for d in data:
#                 doc = frappe.get_doc('Subscription Plan', d.plan)
#                 credit_score = frappe.db.get_value("Customer", self.party, 'custom_credit_assigned_monthly')
#                 credit_allocation(self.party, self.company, credit_score , self.name , row.total_amount)
                



# def credit_allocation(customer, company, credit_score, payment_reference , paid_amount):
    
#cron monthly credit allocation
def monthly_credit_allocation():
    cu_list = frappe.db.get_list("Customer" , pluck="name")
    for row in cu_list:
        customer = frappe.get_doc("Customer", row)
        doc = frappe.new_doc("Credit Allocation")
        doc.customer = row
        doc.credit_score = customer.custom_credit_assigned_monthly
        doc.save(ignore_permissions = True)
        doc.submit()